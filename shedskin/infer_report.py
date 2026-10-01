# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.infer_report: debug reporting for the type analysis

Everything `shedskin.infer2` logs about what it is doing: the allocation
site inventory, the templates created during propagation, what each round
minted and learned, the growth table, and the final signatures per site.
None of it influences the analysis; see the header of `shedskin.infer2` for
how to read a -d3 log and the environment knobs that add to it.
"""

import ast
import logging
import os
from typing import TYPE_CHECKING, Any, NamedTuple, Optional

from . import infer, infer2, python

if TYPE_CHECKING:
    from . import config

logger = logging.getLogger("infer")


# V2_MAX_TEMPLATE_LINES: cap on how many templates are listed individually.
# A large program creates thousands; the counts stay exact, only the listing
# is truncated.
V2_MAX_TEMPLATE_LINES = 200


def report_allocation_sites(
    gx: "config.GlobalInfo", sites: list["infer2.AllocationSite"], builtin_count: int
) -> None:
    """Log the allocation site inventory."""
    by_kind: dict[str, list["infer2.AllocationSite"]] = {}
    for site in sites:
        by_kind.setdefault(site.kind, []).append(site)

    logger.debug("[infer v2: allocation site inventory]")
    logger.debug(
        "  program constructor nodes: %d (builtin scanned: %d)",
        len(sites),
        builtin_count,
    )
    for kind in (infer2.ALLOC_CONTAINER, infer2.ALLOC_INSTANCE, infer2.ALLOC_SCALAR):
        logger.debug("    %-10s %d", kind, len(by_kind.get(kind, [])))

    contoured = by_kind.get(infer2.ALLOC_CONTAINER, []) + by_kind.get(
        infer2.ALLOC_INSTANCE, []
    )
    contoured.sort(
        key=lambda s: (s.module.ident, s.lineno if s.lineno is not None else -1)
    )

    def log_group(header: str, group: list["infer2.AllocationSite"]) -> None:
        if not group:
            return
        logger.debug(header, len(group))
        for site in group:
            logger.debug(
                "    %-20s %-10s dcpa %-4d %-22s %s",
                site.location(),
                site.cl.ident,
                site.dcpa,
                site.scope(),
                site.source(),
            )

    log_group(
        "  module-level allocation sites (%d):",
        [site for site in contoured if site.module_level],
    )
    log_group(
        "  in-function molds (%d), one site per template each:",
        [site for site in contoured if not site.module_level],
    )

    if logger.isEnabledFor(logging.DEBUG):
        for site in by_kind.get(infer2.ALLOC_SCALAR, []):
            logger.debug(
                "    %-20s %-10s scalar    %-22s %s",
                site.location(),
                site.cl.ident,
                site.scope(),
                site.source(),
            )


def format_types(types: infer.Types) -> str:
    """Render a type set as 'cls(contour), cls(contour)'."""
    return ", ".join(
        sorted("%s(%d)" % (cl.ident, dcpa) for cl, dcpa in types)
    ) or "-"


def render_signature(signature: tuple) -> str:
    """Render a signature compactly, for diagnosing what grew."""
    parts = []
    for name, types in signature:
        if not types:
            continue
        rendered = [infer2.render_item(item) for item in sorted(types, key=str)]
        parts.append("%s=%s" % (name, "|".join(rendered)))
    return "{" + " ".join(parts) + "}" if parts else "{}"


class RoundStats(NamedTuple):
    """What one outer round of stage 4 did.

    `minted` is how many discovered in-function sites got a contour of their
    own this round; `waiting` is how many were still without one after the
    mint, deferred ones included. `learned` counts sites whose contour
    gained a type it did not have before. A round that mints nothing and
    learns nothing is the fixpoint.

    `upgrades` is how many contours moved to a larger signature this round,
    which is how a site whose contour was empty comes to be looked up under
    a bigger key. `signatures` is how many distinct signatures exist, which
    is the quantity the number of keys — and so the number of sites — is
    bounded by. Both flattening is convergence.
    """

    round: int
    minted: int
    waiting: int
    learned: int
    templates: int
    contours: int
    upgrades: int
    signatures: int


class TemplateRecord(NamedTuple):
    """One CPA template, and the molds it turns into allocation sites.

    A template is a copy of a function made for one point in the cartesian
    product of its argument types. `dcpa` is the contour of the receiver for a
    method, `cart` the argument types, `cpa` the template number within dcpa.

    `molds` are the constructor nodes written inside the function. Each one
    becomes a real allocation site in this template, at (node, dcpa, cpa), and
    those are the sites the sweep does not yet own: they still take whatever
    contour the shape-keyed guess in gx.list_types gave them.
    """

    func: "python.Function"
    dcpa: int
    cpa: int
    cart: tuple
    molds: list[tuple["infer2.AllocationSite", Optional[tuple["python.Class", int]]]]

    @property
    def builtin(self) -> bool:
        return bool(self.func.mv.module.builtin)

    def name(self) -> str:
        func = self.func
        if isinstance(func.parent, (python.Class, python.StaticClass)):
            base = "%s.%s" % (func.parent.ident, func.ident)
        else:
            base = func.ident
        return "%s.%s" % (func.mv.module.ident, base)

    def signature(self) -> str:
        parts = []
        if self.dcpa:
            parent = getattr(self.func.parent, "ident", "?")
            parts.append("self=%s(%d)" % (parent, self.dcpa))
        parts.extend(format_type(item) for item in self.cart)
        return "(%s)" % ", ".join(parts)


def format_type(item: tuple["python.Class", int]) -> str:
    """Render one (class, contour) pair."""
    cl, dcpa = item
    return "%s(%d)" % (cl.ident, dcpa)


def molds_by_function(
    sites: list["infer2.AllocationSite"],
) -> dict["python.Function", list["infer2.AllocationSite"]]:
    """Group in-function constructor nodes by the function they live in."""
    grouped: dict["python.Function", list["infer2.AllocationSite"]] = {}
    for site in sites:
        if site.kind == infer2.ALLOC_SCALAR or site.module_level:
            continue
        assert isinstance(site.parent, python.Function)
        grouped.setdefault(site.parent, []).append(site)
    return grouped


def collect_templates(
    gx: "config.GlobalInfo", sites: list["infer2.AllocationSite"]
) -> list[TemplateRecord]:
    """Every template that exists in the current network, with its molds."""
    grouped = molds_by_function(sites)
    records = []
    for func in gx.allfuncs:
        for dcpa, carts in func.cp.items():
            for cart, cpa in carts.items():
                molds = []
                for mold in grouped.get(func, []):
                    node = gx.cnode.get((mold.node, dcpa, cpa))
                    if node is None:
                        continue
                    types = node.types()
                    alloc = next(iter(types)) if len(types) == 1 else None
                    molds.append((mold, alloc))
                records.append(
                    TemplateRecord(func, dcpa, cpa, cart, molds)
                )
    # cpa numbering depends on the order templates happened to be created,
    # so it is not a stable tiebreak; the argument signature is a property of
    # the program and is
    records.sort(key=lambda r: (r.builtin, r.name(), r.dcpa, infer2.repr_cart(r.cart)))
    return records


def report_templates(records: list[TemplateRecord]) -> None:
    """Log the templates and the allocation sites they enable."""
    program = [r for r in records if not r.builtin]
    builtin = [r for r in records if r.builtin]
    enabling = [r for r in program if r.molds]
    new_sites = sum(len(r.molds) for r in program)

    logger.debug("[infer v2: templates created during propagation]")
    logger.debug(
        "  templates: %d (program: %d, builtin: %d)",
        len(records),
        len(program),
        len(builtin),
    )
    logger.debug(
        "  %d program template(s) enable %d new allocation site(s)",
        len(enabling),
        new_sites,
    )

    shown = 0
    for record in enabling:
        if shown >= V2_MAX_TEMPLATE_LINES:
            logger.debug(
                "  ... %d more template(s) not listed",
                len(enabling) - shown,
            )
            break
        shown += 1
        logger.debug("  %s%s", record.name(), record.signature())
        for mold, alloc in record.molds:
            logger.debug(
                "      %-20s %-10s %-14s %s",
                mold.location(),
                mold.cl.ident,
                format_type(alloc) if alloc else "?",
                mold.source(),
            )

    per_builtin: dict[str, int] = {}
    for record in builtin:
        per_builtin[record.name()] = per_builtin.get(record.name(), 0) + 1
    if per_builtin:
        logger.debug("  builtin templates by function:")
        for name in sorted(
            per_builtin, key=lambda n: (-per_builtin[n], n)
        )[:V2_MAX_TEMPLATE_LINES]:
            logger.debug("    %-40s %d", name, per_builtin[name])


def report_round_learning(
    core: "infer2.FrozenCore",
    commit: "infer2.CommitResult",
    round_no: int,
) -> None:
    """Log what the module-level sites learned in this round.

    Only what was new to the core. A site that saw the same types again has
    not learned anything, and the round loop stops on exactly that.
    """
    for site, fresh in sorted(
        commit.probe_fresh.items(), key=lambda kv: kv[0].location()
    ):
        cl, contour = core.bindings[site.node]
        logger.debug(
            "  round %d  %-20s %-10s contour %-4d %s",
            round_no,
            site.location(),
            cl.ident,
            contour,
            site.source(),
        )
        for name in sorted(fresh):
            if name in infer2.CONTOUR_SIGNATURE_SKIP:
                continue
            logger.debug("      %-8s <- %s", name, format_types(fresh[name]))


def alloc_id_source(alloc_id: Any) -> str:
    """Render the AST node of an alloc_id as source, for logging."""
    node = alloc_id[2]
    try:
        text = " ".join(ast.unparse(node).split())
    except Exception:  # pragma: no cover - defensive
        return "<%s>" % type(node).__name__
    if len(text) > infer2.ALLOC_SOURCE_MAXLEN:
        text = text[: infer2.ALLOC_SOURCE_MAXLEN - 3] + "..."
    return text


def alloc_id_location(alloc_id: Any) -> str:
    """Render 'function:line' for an alloc_id, for logging."""
    node = alloc_id[2]
    lineno = getattr(node, "lineno", None)
    return "%s:%s" % (alloc_id[0], lineno if lineno is not None else "-")


def report_added_site(
    core: "infer2.FrozenCore",
    added: tuple[Any, tuple["python.Class", int]],
    round_no: int,
) -> None:
    """Log one site this round gave a contour to."""
    key, (cl, contour) = added
    logger.debug(
        "  round %d: +1 site %s  %s  contour %d",
        round_no,
        alloc_id_location(key),
        cl.ident,
        contour,
    )
    logger.debug("      %s   cart %s", alloc_id_source(key), infer2.repr_cart(key[1]))


def report_round(stats: RoundStats) -> None:
    """One line summarising a round, and the numbers a hang would show in."""
    logger.debug(
        "[infer v2: round %d done: %d site(s) minted"
        " (%d waiting), %d learned, %d template(s),"
        " %d contour(s) total]",
        stats.round,
        stats.minted,
        stats.waiting,
        stats.learned,
        stats.templates,
        stats.contours,
    )
    if stats.upgrades:
        logger.debug(
            "  round %d: %d contour(s) moved to a larger signature",
            stats.round,
            stats.upgrades,
        )


def report_growth(history: list[RoundStats]) -> None:
    """The growth curve, which is what tells convergence from a creation cycle.

    A creation cycle shows up as contours and sites climbing round on round
    without the minted count falling off. Convergence shows up as both
    flattening and the last round minting nothing.
    """
    logger.debug("[infer v2: growth per round]")
    logger.debug(
        "    %-6s %-7s %-8s %-8s %-9s %-10s %-7s %-5s",
        "round",
        "minted",
        "waiting",
        "learned",
        "contours",
        "templates",
        "upgrade",
        "sigs",
    )
    for stats in history:
        logger.debug(
            "    %-6d %-7d %-8d %-8d %-9d %-10d %-7d %-5d",
            stats.round,
            stats.minted,
            stats.waiting,
            stats.learned,
            stats.contours,
            stats.templates,
            stats.upgrades,
            stats.signatures,
        )


def report_signature_table(core: "infer2.FrozenCore") -> None:
    """Dump the interned signatures and who holds them (diagnostic)."""
    if not os.environ.get("SS_V2_SIGDUMP"):
        return
    holders: dict[int, list] = {}
    for binding, sid in core.contour_signature.items():
        holders.setdefault(sid, []).append(binding)
    by_id = {v: k for k, v in core.signature_ids.items()}
    logger.debug("[infer v2: signature table: %d signature(s)]", len(by_id))
    for sid in sorted(by_id):
        cl, signature = by_id[sid]
        owners = sorted(holders.get(sid, []), key=lambda cc: cc[1])
        logger.debug(
            "  sig %-4d %-10s held by %d contour(s): %s",
            sid,
            cl.ident,
            len(owners),
            ",".join(str(c) for _cl, c in owners[:12]),
        )
        for name, types in signature:
            logger.debug("        %-8s = %s", name, sorted(str(t) for t in types))


def report_site_signatures(gx: "config.GlobalInfo", core: "infer2.FrozenCore") -> None:
    """Final overview: every allocation site and the signature deduced for it.

    Module-level sites are listed one per line. In-function sites are grouped
    by the mold they came from — one source line can become many sites, one
    per template — and a mold whose sites all settled on the same signature
    is reported once, since that is the interesting fact about it. A mold
    whose sites differ is reported per signature, because that difference is
    the polymorphism the contours exist to keep apart.
    """
    by_id = {v: k for k, v in core.signature_ids.items()}

    def rendered(binding: tuple["python.Class", int]) -> str:
        sid = core.contour_signature.get(binding)
        if sid is None:
            return "(no signature)"
        return render_signature(by_id.get(sid, (None, ()))[1]) or "{}"

    logger.debug("[infer v2: deduced signature per allocation site]")

    if core.bindings:
        logger.debug("  module-level sites (%d):", len(core.bindings))
        for node, binding in sorted(
            core.bindings.items(),
            key=lambda kv: (getattr(kv[0], "lineno", 0), kv[1][1]),
        ):
            logger.debug(
                "    %-4s %-10s contour %-4d %s",
                getattr(node, "lineno", "-"),
                binding[0].ident,
                binding[1],
                rendered(binding),
            )

    molds: dict[tuple, dict[str, list[tuple["python.Class", int]]]] = {}
    for key, binding in core.alloc_bindings.items():
        mold = (key[0], key[2])
        molds.setdefault(mold, {}).setdefault(rendered(binding), []).append(
            binding
        )
    if not molds:
        return
    sites = sum(len(v) for groups in molds.values() for v in groups.values())
    logger.debug(
        "  in-function sites (%d, from %d mold(s)):", sites, len(molds)
    )
    for mold in sorted(molds, key=lambda m: (str(m[0]), getattr(m[1], "lineno", 0))):
        groups = molds[mold]
        node = mold[1]
        where = "%s:%s" % (mold[0], getattr(node, "lineno", "-"))
        source = alloc_id_source((mold[0], (), node))
        count = sum(len(v) for v in groups.values())
        if len(groups) == 1:
            signature, bindings = next(iter(groups.items()))
            logger.debug(
                "    %-24s %-10s %d site(s), 1 signature  %s",
                where,
                bindings[0][0].ident,
                count,
                signature,
            )
        else:
            logger.debug(
                "    %-24s %d site(s), %d signatures",
                where,
                count,
                len(groups),
            )
            for signature in sorted(groups):
                bindings = groups[signature]
                logger.debug(
                    "        %-10s x%-3d %s",
                    bindings[0][0].ident,
                    len(bindings),
                    signature,
                )
        logger.debug("        %s", source)


def report_core(core: "infer2.FrozenCore", rounds: int) -> None:
    """Summarise what the rounds established."""
    report_signature_table(core)
    logger.debug(
        "[infer v2: frozen core after %d round(s): %d module-level site(s),"
        " %d in-function site(s), %d contour(s), %d contour variable(s)]",
        rounds,
        len(core.bindings),
        len(core.alloc_bindings),
        len(core.owned_contours()),
        len(core.contents),
    )
    per_class: dict[str, int] = {}
    for cl, _contour in core.owned_contours():
        per_class[cl.ident] = per_class.get(cl.ident, 0) + 1
    for ident in sorted(per_class):
        logger.debug("    %-10s %d contour(s)", ident, per_class[ident])


def report_upgrades(
    core: "infer2.FrozenCore",
    previous: dict[tuple["python.Class", int], int],
    changed: list[tuple["python.Class", int]],
) -> None:
    """With SS_V2_UPGRADES=1, show how the signatures that moved changed."""
    if not os.environ.get("SS_V2_UPGRADES"):
        return
    by_id = {v: k for k, v in core.signature_ids.items()}
    for binding in changed[:12]:
        was = by_id.get(previous[binding], (None, ()))[1]
        now = by_id.get(core.contour_signature[binding], (None, ()))[1]
        logger.debug(
            "    upgrade %s(%d): %s  ->  %s",
            binding[0].ident,
            binding[1],
            render_signature(was),
            render_signature(now),
        )
    if len(changed) > 12:
        logger.debug("    ... %d more upgrade(s)", len(changed) - 12)
