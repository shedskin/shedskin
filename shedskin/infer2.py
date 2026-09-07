# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.infer2: experimental alternative type analysis ("infer v2")

Enabled with --infer-v2. This is a separate analysis from the CPA/IFA one in
`shedskin.infer`, kept in its own module so the two do not get tangled while
v2 is built up. It reuses infer's constraint graph, propagation and network
backup/restore; everything specific to v2 lives here.
"""

import ast
import logging
import sys
from typing import TYPE_CHECKING, Any, NamedTuple, Optional

from . import infer, python

if TYPE_CHECKING:
    from . import config

logger = logging.getLogger("infer")


# ---------------------------------------------------------------------------
# --- infer v2: experimental alternative analysis (enabled with --infer-v2)
# ---------------------------------------------------------------------------
#
# An alternative to iterative_dataflow_analysis() in shedskin.infer, based on a
# idea about where termination comes from.
#
# IFA reaches a fixpoint by *splitting* contours in response to observed
# imprecision. A split may be undone and redone across rounds, which makes the
# analysis order-dependent and leaves it with no bound other than MAXITERS.
#
# Infer v2 instead treats inference as an append-only accumulation of
# knowledge (a "frozen core" of facts):
#
#   - An allocation site is an AST node. Its identity is fixed by the program
#     text and never changes during analysis.
#   - What accumulates is the set of *instances* of that site: the CNodes
#     (node, dcpa, cpa) created for it, one per template it is analyzed under.
#     A site's signature is never rewritten; a new one is created or an
#     existing one reused.
#   - Facts are only added, never retracted. The fixpoint is then unique and
#     independent of the order in which sites are visited, which also makes a
#     failing program reproducible and therefore reducible.
#
# Termination does not follow from the append-only property by itself. A site
# can keep gaining instances forever if a contour created inside a template of
# f flows back into f's own argument product; that is a cycle in the
# contour-creation graph, and it is what tests like amaze_min.py hit. Breaking
# those cycles is a separate rule, not yet implemented here.
#
# This is being built up in stages. Stage 1 (this code) does no inference of
# its own. It takes an inventory of allocation sites, hands off to the existing
# analysis, and then reports how many instances each site ended up with. That
# census is the measurement needed to tell a creation cycle (a few sites
# climbing without bound) apart from combinatorial blowup (many sites at modest
# counts), which is the question that decides what stage 2 should do.

ALLOC_CONTAINER = "container"  # builtin container: carries contours
ALLOC_INSTANCE = "instance"  # class instance: one contour per class
ALLOC_SCALAR = "scalar"  # int/str/None/..: never gets a contour

# ALLOC_SOURCE_MAXLEN: allocating expressions are logged as source; longer
# ones are truncated so the listing stays one site per line.
ALLOC_SOURCE_MAXLEN = 40

# V2_PROBE_ROUNDS: safety bound on the propagate-to-fixpoint loop used when
# probing a single allocation site. Propagation is monotone, so this should
# not be reached; hitting it means the probe itself is not converging.
V2_PROBE_ROUNDS = 20

# V2_CPA_LIMIT: cartesian product limit used while probing. Deliberately far
# above CPA_LIMIT, since a probe wants the fullest picture of what reaches a
# contour rather than the fastest route to a fixpoint. Still bounded, and a
# probe that hits it is reported as truncated.
V2_CPA_LIMIT = 1000

# V2_MAX_SWEEPS: safety bound on the sweep loop. Each sweep only adds facts,
# so the loop must converge; reaching this means it is not, which is the
# symptom a contour-creation cycle would produce.
V2_MAX_SWEEPS = 20

# V2_MAX_TEMPLATE_LINES: cap on how many templates are listed individually.
# A large program creates thousands; the counts stay exact, only the listing
# is truncated.
V2_MAX_TEMPLATE_LINES = 200


class AllocationSite:
    """A constructor node: an AST expression that creates an object.

    Identified by its CNode at (node, 0, 0). What that node means depends on
    where it is written, and the difference matters:

    - At module level it *is* an allocation site. There is exactly one, it
      exists from the start, and it can be given a contour directly.
    - Inside a function it is only the mold that func_copy copies from. The
      allocation sites are the (node, dcpa, cpa) copies, one per template,
      and before a template exists neither does the site. Giving the mold a
      contour would force every template's copy into one shared contour,
      which is site-keying and loses the polymorphism CPA exists to keep.

    `parent` is the function the node is written in, recorded because the
    contour-creation cycle rule will need it: the question it has to answer
    is whether a contour reaching a function's argument product was created
    inside a template of that same function.
    """

    __slots__ = ("cnode", "cl", "dcpa", "kind", "parent", "module")

    def __init__(
        self, cnode: infer.CNode, cl: "python.Class", dcpa: int, kind: str
    ) -> None:
        self.cnode = cnode
        self.cl = cl
        self.dcpa = dcpa
        self.kind = kind
        self.parent = cnode.parent
        self.module = cnode.mv.module

    @property
    def node(self) -> Any:
        """The AST node that allocates."""
        return self.cnode.thing

    @property
    def module_level(self) -> bool:
        """Whether this node is a real allocation site already.

        False for nodes inside functions, which are molds until templated.
        """
        return not isinstance(self.parent, python.Function)

    @property
    def builtin(self) -> bool:
        """Whether this site lives in a builtin module."""
        return bool(self.module.builtin)

    @property
    def lineno(self) -> Optional[int]:
        """Source line, or None for nodes shedskin synthesized itself."""
        return getattr(self.cnode.thing, "lineno", None)

    def location(self) -> str:
        """Human-readable 'module:line' for this site."""
        lineno = self.lineno
        if lineno is None:
            return "%s:-" % self.module.ident
        return "%s:%d" % (self.module.ident, lineno)

    def source(self, maxlen: int = ALLOC_SOURCE_MAXLEN) -> str:
        """The allocating expression as source, collapsed to one line.

        Shedskin synthesizes nodes that did not come from the source and may
        not be unparseable, so this falls back to the node's type name.
        """
        node = self.cnode.thing
        text = ""
        if isinstance(node, ast.AST):
            try:
                text = ast.unparse(node)
            except Exception:  # pragma: no cover - defensive
                text = ""
        if not text:
            return "<%s>" % type(node).__name__
        text = " ".join(text.split())
        if len(text) > maxlen:
            text = text[: maxlen - 3] + "..."
        return text

    def scope(self) -> str:
        """Human-readable name of the enclosing function, or '<module>'."""
        func = self.parent
        if not isinstance(func, python.Function):
            return "<module>"
        if isinstance(func.parent, (python.Class, python.StaticClass)):
            return "%s.%s" % (func.parent.ident, func.ident)
        return func.ident

    def __repr__(self) -> str:
        return "<AllocationSite %s %s(%d) %s %s>" % (
            self.location(),
            self.cl.ident,
            self.dcpa,
            self.kind,
            self.source(),
        )


def allocation_site_kind(cl: "python.Class") -> str:
    """Classify an allocation site by the class it allocates."""
    if cl.mv.module.builtin and cl.ident in infer.SPLIT_CLASS_IDENTS:
        return ALLOC_CONTAINER
    if cl.ident in infer.SCALAR_CLASS_IDENTS:
        return ALLOC_SCALAR
    return ALLOC_INSTANCE


def allocation_site_type(
    gx: "config.GlobalInfo", cnode: infer.CNode
) -> Optional[tuple["python.Class", int]]:
    """The (class, dcpa) a constructor node allocates, or None.

    iterative_dataflow_analysis() clears the types of container constructor
    nodes inside functions between rounds, so after analysis gx.types no
    longer answers this for every site. gx.orig_types holds the pre-analysis
    snapshot and does, which lets the inventory be taken at either point.
    """
    for table in (gx.types, gx.orig_types):
        types = table.get(cnode, set())
        if len(types) == 1:
            cl, dcpa = next(iter(types))
            if isinstance(cl, python.Class):
                return (cl, dcpa)
    return None


def collect_allocation_sites(
    gx: "config.GlobalInfo", builtins: bool = False
) -> list[AllocationSite]:
    """Collect the base allocation sites of the program.

    A base site is a constructor CNode at (node, 0, 0); copies made for
    templates are instances of it and are not returned here. Builtin-module
    sites are scanned but only included when `builtins` is true.

    The result is sorted deterministically, so that two runs over the same
    program produce the same listing.
    """
    sites = []
    for (_thing, dcpa, cpa), cnode in gx.cnode.items():
        if not cnode.constructor or dcpa != 0 or cpa != 0:
            continue
        if not builtins and cnode.mv.module.builtin:
            continue
        site_type = allocation_site_type(gx, cnode)
        if site_type is None:
            # a constructor node should allocate exactly one class; anything
            # else is not something this inventory can describe
            continue
        cl, site_dcpa = site_type
        sites.append(
            AllocationSite(cnode, cl, site_dcpa, allocation_site_kind(cl))
        )

    def sort_key(site: AllocationSite) -> tuple[Any, ...]:
        return (
            site.module.ident,
            site.lineno if site.lineno is not None else -1,
            getattr(site.cnode.thing, "col_offset", -1),
            type(site.cnode.thing).__name__,
            site.cl.ident,
            site.dcpa,
        )

    sites.sort(key=sort_key)
    return sites


def allocation_site_instances(
    gx: "config.GlobalInfo",
) -> dict[Any, set[tuple[int, int]]]:
    """Map each allocation site's AST node to its (dcpa, cpa) instances.

    This is the contour census: how many copies of each site the analysis
    ended up creating. Called after analysis, it is the log that distinguishes
    a creation cycle (a few sites with unbounded counts) from combinatorial
    blowup (many sites with modest counts).
    """
    instances: dict[Any, set[tuple[int, int]]] = {}
    for (thing, dcpa, cpa), cnode in gx.cnode.items():
        if cnode.constructor:
            instances.setdefault(thing, set()).add((dcpa, cpa))
    return instances


def report_allocation_sites(
    gx: "config.GlobalInfo", sites: list[AllocationSite], builtin_count: int
) -> None:
    """Log the allocation site inventory."""
    by_kind: dict[str, list[AllocationSite]] = {}
    for site in sites:
        by_kind.setdefault(site.kind, []).append(site)

    logger.info("[infer v2: allocation site inventory]")
    logger.info(
        "  program constructor nodes: %d (builtin scanned: %d)",
        len(sites),
        builtin_count,
    )
    for kind in (ALLOC_CONTAINER, ALLOC_INSTANCE, ALLOC_SCALAR):
        logger.info("    %-10s %d", kind, len(by_kind.get(kind, [])))

    contoured = by_kind.get(ALLOC_CONTAINER, []) + by_kind.get(ALLOC_INSTANCE, [])
    contoured.sort(
        key=lambda s: (s.module.ident, s.lineno if s.lineno is not None else -1)
    )

    def log_group(header: str, group: list[AllocationSite]) -> None:
        if not group:
            return
        logger.info(header, len(group))
        for site in group:
            logger.info(
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
        for site in by_kind.get(ALLOC_SCALAR, []):
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


def v2_propagate(gx: "config.GlobalInfo") -> int:
    """Propagate to a fixpoint, with the incremental heuristics switched off.

    iterative_dataflow_analysis() only lets a few new functions and allocation
    sites into the analysis per round, to keep CPA from exploding early. A
    probe wants the whole program instead, so the counters are pushed out of
    range rather than reset each round.
    """
    rounds = 0
    gx.cpa_limited = False
    while rounds < V2_PROBE_ROUNDS:
        rounds += 1
        # gx.cpa_limit defaults to 0, which would limit away every call and
        # leave the program untemplated
        gx.cpa_limit = V2_CPA_LIMIT
        gx.added_funcs = -sys.maxsize
        gx.added_allocs = -sys.maxsize
        gx.new_alloc_info = {}
        before = sum(len(types) for types in gx.types.values())
        infer.propagate(gx)
        gx.alloc_info.update(gx.new_alloc_info)
        if sum(len(types) for types in gx.types.values()) == before:
            break
    return rounds


def contour_variables(
    gx: "config.GlobalInfo", cl: "python.Class", contour: int
) -> dict[str, infer.CNode]:
    """The variable nodes belonging to one contour of a class."""
    nodes = {}
    for var in cl.vars.values():
        node = gx.cnode.get((var, contour, 0))
        if node is not None:
            nodes[var.name] = node
    return nodes


class ProbeResult(NamedTuple):
    """What probing one allocation site found.

    `reached` is false when the site never allocated its contour at all,
    because nothing propagated into the function holding it yet. That is not
    the same as a site nothing flows into, and the two must not be reported
    alike: one is a fact about the program, the other just means the call
    graph has not been discovered that far.
    """

    contour: int
    inflow: dict[str, infer.Types]
    rounds: int
    reached: bool


def site_allocated(
    gx: "config.GlobalInfo", site: AllocationSite, contour: int
) -> bool:
    """Whether the site actually allocated the given contour anywhere."""
    wanted = (site.cl, contour)
    for (thing, _dcpa, _cpa), node in gx.cnode.items():
        if thing is site.node and wanted in node.types():
            return True
    return False


class FrozenCore:
    """Append-only knowledge accumulated across sweeps.

    Two tables. `bindings` says which contour a site owns, allocated once and
    never reassigned. `contents` says what has been learned to flow into each
    contour's variables. Both only ever grow; nothing is retracted, which is
    what makes the fixpoint independent of the order sites are visited in.
    """

    def __init__(self) -> None:
        self.bindings: dict[Any, tuple["python.Class", int]] = {}
        self.contents: dict[tuple["python.Class", int, str], infer.Types] = {}
        self.next_contour: dict["python.Class", int] = {}

    def contour_for(
        self, site: AllocationSite, baseline_dcpa: dict["python.Class", int]
    ) -> int:
        """The contour this site owns, allocating one on first use."""
        binding = self.bindings.get(site.node)
        if binding is not None:
            return binding[1]
        cl = site.cl
        contour = self.next_contour.setdefault(cl, baseline_dcpa[cl])
        self.next_contour[cl] = contour + 1
        self.bindings[site.node] = (cl, contour)
        return contour

    def open_contours(self) -> set[tuple["python.Class", int]]:
        """Contours that may receive inflow: every committed site's own."""
        return set(self.bindings.values())

    def learn(
        self, cl: "python.Class", contour: int, name: str, types: infer.Types
    ) -> infer.Types:
        """Add types to a contour variable; return the ones that were new."""
        key = (cl, contour, name)
        known = self.contents.setdefault(key, set())
        new = types - known
        known |= new
        return new


def apply_core(
    gx: "config.GlobalInfo",
    core: FrozenCore,
    baseline_dcpa: dict["python.Class", int],
) -> None:
    """Rebuild the committed contours on top of a freshly restored network."""
    for cl, dcpa in baseline_dcpa.items():
        cl.dcpa = dcpa
    for cl, nxt in core.next_contour.items():
        cl.dcpa = max(cl.dcpa, nxt)

    for cl, contour in set(core.bindings.values()):
        infer.class_copy(gx, cl, contour)

    for cnode_thing, (cl, contour) in core.bindings.items():
        cnode = gx.cnode.get((cnode_thing, 0, 0))
        if cnode is not None:
            gx.types[cnode] = {(cl, contour)}

    for (cl, contour, name), types in core.contents.items():
        node = contour_variables(gx, cl, contour).get(name)
        if node is not None:
            gx.types.setdefault(node, set()).update(types)


def probe_allocation_site(
    gx: "config.GlobalInfo",
    site: AllocationSite,
    core: Optional[FrozenCore] = None,
    baseline_dcpa: Optional[dict["python.Class", int]] = None,
) -> ProbeResult:
    """Give one allocation site a contour of its own and see what flows in.

    The site allocates a contour nothing else uses, and the program is then
    propagated. Whatever ends up in that contour's variables came from this
    site and nowhere else, which is what makes the result attributable.

    Contours outside the open set are frozen for the duration: they still
    propagate what they already hold, but cannot receive anything new. Without
    that, a probe is just an unsplit analysis of the whole program, and every
    container merges into every other one; what arrives then says more about
    the absence of splitting than about the site. The open set is the sites
    already committed to the core plus this one, so it widens as the core
    fills in and the freeze dissolves as coverage grows.

    Only module-level sites can be probed this way. A node inside a function
    has no site until a template exists, and its contour belongs in
    gx.alloc_info keyed by (function, cartesian product, node) rather than by
    the node alone.

    The network is restored afterwards. Only the core survives a probe, so
    what one probe passes to the next is exactly what it committed.
    """
    assert site.module_level, "only module-level sites can be probed directly"
    assert site.kind == ALLOC_CONTAINER, "only builtin containers are split"

    standalone = core is None
    if core is None:
        core = FrozenCore()
    if baseline_dcpa is None:
        baseline_dcpa = {cl: cl.dcpa for cl in gx.allclasses}

    cl = site.cl
    saved_dcpa = dict(baseline_dcpa)
    saved_alloc_info = gx.alloc_info.copy()
    saved_orig_types = gx.orig_types
    backup = infer.backup_network(gx)

    apply_core(gx, core, baseline_dcpa)
    contour = core.contour_for(site, baseline_dcpa)
    infer.class_copy(gx, cl, contour)
    cl.dcpa = max(cl.dcpa, contour + 1)
    gx.types[site.cnode] = {(cl, contour)}

    gx.orig_types = {node: types.copy() for node, types in gx.types.items()}

    # what the contour holds before propagation, so the result shows what
    # arrived rather than what the core already knew
    seeded = {
        name: node.types().copy()
        for name, node in contour_variables(gx, cl, contour).items()
    }

    gx.infer_v2_open_contours = core.open_contours() | {(cl, contour)}
    try:
        rounds = v2_propagate(gx)
        reached = site_allocated(gx, site, contour)
        inflow = {}
        for name, node in contour_variables(gx, cl, contour).items():
            arrived = node.types() - seeded.get(name, set())
            if arrived:
                inflow[name] = arrived
    finally:
        gx.infer_v2_open_contours = None
        infer.restore_network(gx, backup)
        gx.alloc_info = saved_alloc_info
        gx.orig_types = saved_orig_types
        for klass, dcpa in saved_dcpa.items():
            klass.dcpa = dcpa
        if standalone:
            core.bindings.pop(site.node, None)

    return ProbeResult(contour, inflow, rounds, reached)


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
    molds: list[tuple[AllocationSite, Optional[tuple["python.Class", int]]]]

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
    sites: list[AllocationSite],
) -> dict["python.Function", list[AllocationSite]]:
    """Group in-function constructor nodes by the function they live in."""
    grouped: dict["python.Function", list[AllocationSite]] = {}
    for site in sites:
        if site.kind == ALLOC_SCALAR or site.module_level:
            continue
        assert isinstance(site.parent, python.Function)
        grouped.setdefault(site.parent, []).append(site)
    return grouped


def collect_templates(
    gx: "config.GlobalInfo", sites: list[AllocationSite]
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
    records.sort(key=lambda r: (r.builtin, r.name(), r.dcpa, r.cpa))
    return records


def report_templates(records: list[TemplateRecord]) -> None:
    """Log the templates and the allocation sites they enable."""
    program = [r for r in records if not r.builtin]
    builtin = [r for r in records if r.builtin]
    enabling = [r for r in program if r.molds]
    new_sites = sum(len(r.molds) for r in program)

    logger.info("[infer v2: templates created during propagation]")
    logger.info(
        "  templates: %d (program: %d, builtin: %d)",
        len(records),
        len(program),
        len(builtin),
    )
    logger.info(
        "  %d program template(s) enable %d new allocation site(s)",
        len(enabling),
        new_sites,
    )

    shown = 0
    for record in enabling:
        if shown >= V2_MAX_TEMPLATE_LINES:
            logger.info(
                "  ... %d more template(s) not listed",
                len(enabling) - shown,
            )
            break
        shown += 1
        logger.info("  %s%s", record.name(), record.signature())
        for mold, alloc in record.molds:
            logger.info(
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
        logger.info("  builtin templates by function:")
        for name in sorted(
            per_builtin, key=lambda n: (-per_builtin[n], n)
        )[:V2_MAX_TEMPLATE_LINES]:
            logger.info("    %-40s %d", name, per_builtin[name])


def sweep_once(
    gx: "config.GlobalInfo",
    probes: list[AllocationSite],
    core: FrozenCore,
    baseline_dcpa: dict["python.Class", int],
    probes_and_molds: Optional[list[AllocationSite]] = None,
    collect: bool = False,
    freeze: bool = True,
) -> tuple[
    dict[AllocationSite, dict[str, infer.Types]],
    int,
    int,
    list[TemplateRecord],
]:
    """One propagation with every bound contour open; read them all.

    Each site owns a contour nothing else uses, so what lands in a contour is
    attributable to its site whether one site is open or all of them are.
    Opening them together means one propagation per sweep instead of one per
    site, and it costs nothing in attribution.

    Molds stay frozen. They have no contours of their own, so letting them
    receive inflow would merge unrelated sites through the shape-keyed
    buckets in gx.list_types, which is what made early probes report every
    class in the program flowing into one list.
    """
    saved_dcpa = dict(baseline_dcpa)
    saved_alloc_info = gx.alloc_info.copy()
    saved_orig_types = gx.orig_types
    backup = infer.backup_network(gx)

    apply_core(gx, core, baseline_dcpa)
    for site in probes:
        contour = core.contour_for(site, baseline_dcpa)
        infer.class_copy(gx, site.cl, contour)
        site.cl.dcpa = max(site.cl.dcpa, contour + 1)
        gx.types[site.cnode] = {(site.cl, contour)}

    gx.orig_types = {node: types.copy() for node, types in gx.types.items()}

    seeded = {}
    for site in probes:
        contour = core.bindings[site.node][1]
        seeded[site.node] = {
            name: node.types().copy()
            for name, node in contour_variables(gx, site.cl, contour).items()
        }

    # Freezing keeps unowned sites from merging into each other, which is
    # what a sweep needs. A pass that only wants to see which templates the
    # program creates must not freeze: blocking writes into object attributes
    # starves calls of their argument types, and a call with no argument types
    # forms no cartesian product and so no template.
    gx.infer_v2_open_contours = core.open_contours() if freeze else None
    try:
        rounds = v2_propagate(gx)
        results: dict[AllocationSite, dict[str, infer.Types]] = {}
        unreached = 0
        for site in probes:
            contour = core.bindings[site.node][1]
            if not site_allocated(gx, site, contour):
                unreached += 1
                continue
            inflow = {}
            for name, node in contour_variables(gx, site.cl, contour).items():
                arrived = node.types() - seeded[site.node].get(name, set())
                if arrived:
                    inflow[name] = arrived
            results[site] = inflow
        templates = collect_templates(gx, probes_and_molds) if collect else []
    finally:
        gx.infer_v2_open_contours = None
        infer.restore_network(gx, backup)
        gx.alloc_info = saved_alloc_info
        gx.orig_types = saved_orig_types
        for klass, dcpa in saved_dcpa.items():
            klass.dcpa = dcpa

    return results, rounds, unreached, templates


def probe_allocation_sites(
    gx: "config.GlobalInfo", sites: list[AllocationSite]
) -> FrozenCore:
    """Sweep over the module-level container sites until nothing is learned.

    Every site is given its contour before the first sweep, not when it first
    learns something. Otherwise a site probed early sees its neighbours still
    sitting in their shape-keyed default contours and records that as a fact;
    the core is append-only, so a contour learned before its owner was bound
    can never be taken back.

    A site whose contents only arrive through some object's attribute cannot
    learn anything until that attribute has been populated by another site,
    which is why one sweep is not enough and why the loop runs until a whole
    sweep is silent.

    Only builtin containers are probed. User classes get one contour each and
    are never split, so giving one a contour of its own says nothing that the
    existing contour does not already say.

    In-function molds are not sites yet and are left out; they become sites
    when templates are created, which is the next stage.
    """
    containers = [site for site in sites if site.kind == ALLOC_CONTAINER]
    probes = [site for site in containers if site.module_level]
    molds = len(containers) - len(probes)
    logger.info(
        "[infer v2: sweeping %d module-level container site(s);"
        " %d in-function mold(s) left for later]",
        len(probes),
        molds,
    )

    core = FrozenCore()
    baseline_dcpa = {cl: cl.dcpa for cl in gx.allclasses}
    for site in probes:
        core.contour_for(site, baseline_dcpa)

    sweep = 0
    while sweep < V2_MAX_SWEEPS:
        sweep += 1
        results, rounds, unreached, _templates = sweep_once(
            gx, probes, core, baseline_dcpa
        )

        learned = 0
        for site, inflow in results.items():
            contour = core.bindings[site.node][1]
            fresh = {}
            for name, types in inflow.items():
                new = core.learn(site.cl, contour, name, types)
                if new:
                    fresh[name] = new
            if not fresh:
                continue
            learned += 1
            logger.info(
                "  sweep %d  %-20s %-10s contour %-4d %s",
                sweep,
                site.location(),
                site.cl.ident,
                contour,
                site.source(),
            )
            for name in sorted(fresh):
                logger.info("      %-8s <- %s", name, format_types(fresh[name]))

        logger.info(
            "  sweep %d: %d site(s) learned something%s (%d propagation round(s))",
            sweep,
            learned,
            ", %d not reached" % unreached if unreached else "",
            rounds,
        )
        if not learned:
            break
    else:
        logger.warning(
            "infer v2: stopped after %d sweeps without converging",
            V2_MAX_SWEEPS,
        )

    report_core(core, sweep)

    # one more propagation, this time keeping the templates it creates, so the
    # molds that become allocation sites inside them can be listed
    _results, _rounds, _unreached, templates = sweep_once(
        gx,
        probes,
        core,
        baseline_dcpa,
        probes_and_molds=sites,
        collect=True,
        freeze=False,
    )
    report_templates(templates)
    return core


def report_core(core: FrozenCore, sweeps: int) -> None:
    """Summarise what the sweeps established."""
    logger.info(
        "[infer v2: frozen core after %d sweep(s): %d site(s), %d contour"
        " variable(s) learned]",
        sweeps,
        len(core.bindings),
        len(core.contents),
    )
    per_class: dict[str, int] = {}
    for cl, _contour in core.bindings.values():
        per_class[cl.ident] = per_class.get(cl.ident, 0) + 1
    for ident in sorted(per_class):
        logger.info("    %-10s %d contour(s)", ident, per_class[ident])


def infer_v2_analysis(gx: "config.GlobalInfo") -> None:
    """Experimental alternative entry point to iterative_dataflow_analysis.

    Stage 1: inventory the constructor nodes, separating module-level
        allocation sites from in-function molds.
    Stage 2: sweep the module-level sites, each owning a contour of its own,
        committing what flows in to an append-only core until a whole sweep
        learns nothing.
    Stage 3: propagate once more and keep the templates, so the molds that
        become allocation sites inside them can be listed.

    There is no stage that infers enough to generate code, so this stops here
    rather than falling back to the existing analysis. Run without --infer-v2
    to compile.
    """
    all_sites = collect_allocation_sites(gx, builtins=True)
    sites = [site for site in all_sites if not site.builtin]
    builtin_count = len(all_sites) - len(sites)
    report_allocation_sites(gx, sites, builtin_count)
    probe_allocation_sites(gx, sites)

    logger.info("[infer v2: stopping after inspection; no C++ is generated]")
    sys.exit(0)
