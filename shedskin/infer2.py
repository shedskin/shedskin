# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.infer2: experimental alternative type analysis ("infer v2")

Enabled with --infer-v2. This is a separate analysis from the CPA/IFA one in
`shedskin.infer`, kept in its own module so the two do not get tangled while
v2 is built up. It reuses infer's constraint graph, propagation and network
backup/restore; everything specific to v2 lives here.
"""

import ast
import os
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
# contour-creation graph, and it is what tests like amaze_min.py hit. Every
# type involved can be non-recursive and one level deep: what is unbounded is
# the supply of distinct *contour identities* for one shape, since each
# template is entitled to mint its own and a signature is keyed by contour
# rather than by shape. Memoization only helps once a signature repeats, and
# such a cycle never produces the same signature twice.
#
# The rule that cuts it is to merge contours whose settled signatures are
# equal ("pre-merging"). That is safe only because of *when* it is done. A
# merge is a binding decision, and bindings are append-only like everything
# else, so committing one against a contour that is still mid-propagation
# risks locking in a comparison made on incomplete information. So a contour
# minted for a newly discovered site is *provisional*: it is scratch for the
# duration of one sweep, it is committed only once that sweep has stopped
# learning, and only then is it compared against the settled core. Contents
# are different and may grow freely at any time; every site pointing at a
# contour sees the richer contents automatically, because it references the
# contour rather than holding a copy.
#
# The stages:
#
#   1. Inventory the constructor nodes, separating module-level allocation
#      sites from in-function molds.
#   2. Sweep the module-level sites over a frozen core until a whole sweep
#      learns nothing.
#   3. Propagate unfrozen and keep the templates, so the molds that become
#      allocation sites inside them can be seen.
#   4. Let those molds become sites: give each one a contour of its own when
#      its template is created, sweep again so they learn, and merge the ones
#      whose settled signatures agree. Repeat, because new sites feed argument
#      products and products key new templates. This is the feedback loop the
#      earlier stages deliberately cut, so growth per round is logged from the
#      start: a hang should be diagnosable rather than mysterious.

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

# V2_MAX_ROUNDS: safety bound on the outer loop. A round is one sweep to
# convergence plus at most one new allocation site, so this is really a
# budget on how many in-function sites may be added; the loop should stop on
# its own well before it, by running out of sites to add. It is large
# because one site per round is the point: a site is named by the signatures
# of the contours around it, and adding several at once shifts the very
# signatures the others were named under.
V2_MAX_ROUNDS = int(os.environ.get("SS_V2_ROUNDS", 20000))




# V2_MAX_TEMPLATE_LINES: cap on how many templates are listed individually.
# A large program creates thousands; the counts stay exact, only the listing
# is truncated.
V2_MAX_TEMPLATE_LINES = 200

# V2_MAX_SITE_LINES: cap on how many newly bound in-function sites are listed
# individually per round.
V2_MAX_SITE_LINES = 60

# V2_SIGNATURE_ROUNDS: bound on the signature fixpoint. A signature is
# written in terms of the signatures of what it contains, so the map is
# recomputed until it stops changing: contours of depth 0 settle first, then
# those mentioning them. Containers cannot nest recursively, so the number of
# layers needed is the nesting depth.
V2_SIGNATURE_ROUNDS = 12

# V2_SITES_PER_ROUND: how many newly discovered allocation sites are given a
# contour per round. Unlimited by default: every site discovered in a round
# is minted at its end. One per round is the conservative schedule the design
# was written against — see FrozenCore.mint_batch — and SS_V2_SITES_PER_ROUND
# sets a finite batch size to fall back to it when a program churns. Each
# round costs a propagation to convergence; the growth table says whether the
# batch size cost anything.


def sites_per_round(value: Optional[str] = None) -> int:
    """Batch size for FrozenCore.mint_batch from SS_V2_SITES_PER_ROUND.

    Unset or empty means unlimited (sys.maxsize); otherwise a positive
    integer.
    """
    if value is None:
        value = os.environ.get("SS_V2_SITES_PER_ROUND", "")
    value = value.strip()
    if not value:
        return sys.maxsize
    limit = int(value)
    if limit < 1:
        raise ValueError("SS_V2_SITES_PER_ROUND must be a positive integer")
    return limit


V2_SITES_PER_ROUND = sites_per_round()


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

        A list comprehension is compiled as a function, but a comprehension
        written at module level runs exactly once and is never templated, so
        an allocation inside one is a real site and not a mold. Left as a
        mold it would wait forever for a template that never comes: it keeps
        the shared bucket contour, which is frozen and so stays empty, and
        whatever reads it gets nothing. That is what
        `board = [[0 for x in range(3)] for y in range(3)]` at module level
        did — `board`'s unit held an empty contour and iterating a row gave
        "variable has no type", while the identical expression inside a
        function was fine. python.outer_func skips comprehensions for
        exactly this reason.
        """
        if not isinstance(self.parent, python.Function):
            return True
        return python.outer_func(self.parent) is None

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

    logger.debug("[infer v2: allocation site inventory]")
    logger.debug(
        "  program constructor nodes: %d (builtin scanned: %d)",
        len(sites),
        builtin_count,
    )
    for kind in (ALLOC_CONTAINER, ALLOC_INSTANCE, ALLOC_SCALAR):
        logger.debug("    %-10s %d", kind, len(by_kind.get(kind, [])))

    contoured = by_kind.get(ALLOC_CONTAINER, []) + by_kind.get(ALLOC_INSTANCE, [])
    contoured.sort(
        key=lambda s: (s.module.ident, s.lineno if s.lineno is not None else -1)
    )

    def log_group(header: str, group: list[AllocationSite]) -> None:
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


def render_signature(signature: tuple) -> str:
    """Render a signature compactly, for diagnosing what grew."""
    parts = []
    for name, types in signature:
        if not types:
            continue
        rendered = []
        for item in sorted(types, key=str):
            if isinstance(item, tuple) and len(item) == 3 and item[1] == "sig":
                rendered.append("%s#%s" % (item[0].ident, item[2]))
            elif isinstance(item, tuple) and len(item) == 2:
                ident = getattr(item[0], "ident", item[0])
                rendered.append("%s(%s)" % (ident, item[1]))
            else:
                rendered.append(str(item))
        parts.append("%s=%s" % (name, "|".join(rendered)))
    return "{" + " ".join(parts) + "}" if parts else "{}"


def empty_contents(cl: "python.Class") -> dict[str, infer.Types]:
    """The contents of a contour that has not received anything yet."""
    return {
        name: set()
        for name in getattr(cl, "vars", {})
        if name not in CONTOUR_SIGNATURE_SKIP
    }


def canonical_key_sort(key: Any) -> tuple:
    """A deterministic order for site keys, which are not comparable as-is.

    Keys hold AST nodes and class objects, so sorting them directly would
    depend on object addresses and make the analysis order-dependent for no
    reason. Rendering them makes the order a property of the program text.
    """
    function, cart, node = key
    return (
        str(function),
        getattr(node, "lineno", 0),
        getattr(node, "col_offset", 0),
        repr_cart(cart),
    )


def repr_cart(cart: Any) -> str:
    """Render a cartesian product for ordering and logging."""
    if not isinstance(cart, tuple):
        return str(cart)
    parts = []
    for item in cart:
        if isinstance(item, tuple) and len(item) == 3 and item[1] == "sig":
            parts.append("%s#%s" % (getattr(item[0], "ident", item[0]), item[2]))
        elif isinstance(item, tuple) and len(item) == 2:
            parts.append("%s(%s)" % (getattr(item[0], "ident", item[0]), item[1]))
        else:
            parts.append(str(item))
    return ",".join(parts)


class FrozenCore:
    """Append-only knowledge accumulated across sweeps.

    Three tables. `bindings` says which contour a module-level site owns.
    `alloc_bindings` says the same for an in-function site, keyed by the
    (function, cartesian product, node) triple that identifies one mold
    inside one template — the same key `ifa_seed_template` looks up, so a
    committed binding is simply handed to it. `contents` says what has been
    learned to flow into each contour's variables. All three only ever grow;
    nothing committed is retracted, which is what makes the fixpoint
    independent of the order sites are visited in.

    `provisional` is not one of them. It holds the contours minted for sites
    discovered during the sweep that is currently running, and it is scratch:
    those contours have not been compared against anything yet, because
    nothing has settled while a sweep is still in progress. `commit_round`
    empties it, either by merging a contour into one whose settled signature
    it matches or by promoting it to a binding of its own.
    """

    def __init__(self) -> None:
        self.bindings: dict[Any, tuple["python.Class", int]] = {}
        self.alloc_bindings: dict[Any, tuple["python.Class", int]] = {}
        self.contents: dict[tuple["python.Class", int, str], infer.Types] = {}
        self.next_contour: dict["python.Class", int] = {}
        self.provisional: dict[Any, tuple["python.Class", int]] = {}
        self.baseline_dcpa: dict["python.Class", int] = {}
        self.open_set: Optional[set[tuple["python.Class", int]]] = None
        # sites seen during the round's propagation that the core has no
        # contour for yet; minted between rounds, never during one
        self.discovered: dict[Any, "python.Class"] = {}
        # signature interning. `signature_ids` gives each distinct settled
        # signature a small number, and `contour_signature` says which one
        # each owned contour currently has. Together they turn a cartesian
        # product full of contour numbers into a key in which two contours
        # that hold the same thing look the same.
        self.signature_ids: dict[tuple[Any, tuple], int] = {}
        self.contour_signature: dict[tuple["python.Class", int], int] = {}
        self.upgrades = 0
        # the cartesian product each binding was actually created for. A key
        # is a *name* derived from signatures, and signatures move; the raw
        # product does not, so it is what lets a site keep its contour when
        # its name changes.
        self.raw_ids: dict[Any, Any] = {}
        self.misses = 0

    # --- contour allocation

    def new_contour(self, cl: "python.Class") -> int:
        """Mint an unused contour number for a class."""
        contour = self.next_contour.setdefault(
            cl, self.baseline_dcpa.get(cl, cl.dcpa)
        )
        self.next_contour[cl] = contour + 1
        return contour

    def contour_for(
        self, site: AllocationSite, baseline_dcpa: dict["python.Class", int]
    ) -> int:
        """The contour a module-level site owns, allocating one on first use."""
        binding = self.bindings.get(site.node)
        if binding is not None:
            return binding[1]
        if not self.baseline_dcpa:
            self.baseline_dcpa = dict(baseline_dcpa)
        contour = self.new_contour(site.cl)
        self.bindings[site.node] = (site.cl, contour)
        return contour

    # --- keys

    def signature_id(self, cl: "python.Class", signature: tuple) -> int:
        """Intern a settled signature, so equal ones get the same number."""
        key = (cl, signature)
        got = self.signature_ids.get(key)
        if got is None:
            got = len(self.signature_ids)
            self.signature_ids[key] = got
        return got

    def canonical(self, item: Any) -> Any:
        """Rewrite one cartesian product entry into signature terms.

        A contour the core owns stands for whatever it has been learned to
        hold, so it is written as its signature: two contours holding the
        same thing become the same entry. Anything else — a user class
        receiver, a scalar, a contour nobody owns — is left alone, since
        there is no signature to speak of and its own identity is already
        the right one.

        This is where merging happens, and it is the only place. No contour
        is ever merged into another, so nothing that flowed into one site
        can appear in another's inflow; what merges is the *name* two sites
        are looked up under, which is derived fresh each round and so is
        allowed to change when a signature grows.
        """
        got = self.contour_signature.get(item)
        if got is None:
            return item
        return (item[0], "sig", got)

    def canonical_key(self, alloc_id: Any) -> Any:
        """The core's name for one in-function allocation site."""
        function, cart, node = alloc_id
        if isinstance(cart, tuple):
            cart = tuple(self.canonical(item) for item in cart)
        return (function, cart, node)

    def rekey(self) -> int:
        """Rename every binding under the current signatures.

        A site is named by the signatures of the contours in its cartesian
        product, and signatures grow, so the same allocation presents under a
        different name as the analysis learns. Left alone, the binding stays
        filed under the old name: the site is rediscovered, minted a second
        contour, and the old one is stranded — empty, unreachable, and still
        served to whoever happens to look it up under the stale name. That
        stranding is what "variable has no type" was.

        Dropping the stale entry instead does not work either. The contour
        goes with it, so the site has to be found again from scratch, which
        changes signatures, which changes names, which strands more entries:
        on a three-line program that cycles forever, four sites discovered
        and pruned every round without end.

        So neither keep nor drop — rename. The contour is what the site owns
        and it never moves; only the name it is filed under changes. Nothing
        is rediscovered, nothing is re-minted, and nothing is stranded. Two
        products that now canonicalise together are one site, and keep the
        older contour.
        """
        renamed: dict[Any, tuple["python.Class", int]] = {}
        raw: dict[Any, Any] = {}
        moved = 0
        for key, binding in self.alloc_bindings.items():
            product = self.raw_ids.get(key)
            fresh = self.canonical_key(product) if product is not None else key
            if fresh != key:
                moved += 1
            if fresh in renamed and renamed[fresh] != binding:
                # Two products that now canonicalise together. Do not merge
                # them: dropping one contour means its site is discovered
                # again next round and minted afresh, which changes contents,
                # which changes signatures, which makes the two products
                # canonicalise apart again — life cycled between 29 and 68
                # rediscovered sites forever on exactly this. Leave this
                # binding under the name it already has; renaming is only
                # ever an improvement, never a loss.
                renamed[key] = binding
                if product is not None:
                    raw[key] = product
                continue
            renamed[fresh] = binding
            if product is not None:
                raw[fresh] = product
        self.alloc_bindings = renamed
        self.raw_ids = raw
        return moved

    def resignature(
        self,
        contents: dict[tuple["python.Class", int], dict[str, infer.Types]],
    ) -> int:
        """Recompute every contour's signature after a round.

        A signature is written in terms of the signatures of what it
        contains, not the contour numbers: a list holding tuple2(11) and a
        list holding tuple2(13) are the same list when those two tuples hold
        the same thing.

        Each pass reads a *snapshot* and writes a scratch map that is
        swapped in at the end. Updating in place while `canonical` reads the
        same dict means a signature is built from a mixture of this pass's
        ids and the last pass's, so the mixture — not the contents — decides
        the id. Every round then produces a fresh mixture, every list gets a
        fresh signature, every site a fresh key, and the site set grows by
        one contour per round forever. That was the amaze_min
        non-termination, and it was this, not a cycle.

        Signatures only grow, because contents only grow, so a contour moves
        up the lattice and never back down; the number of passes needed is
        the nesting depth, which is finite because containers cannot nest
        recursively.
        """
        subjects = sorted(
            set(contents) | self.owned_contours(),
            key=lambda cc: (cc[0].ident, cc[1]),
        )
        previous = dict(self.contour_signature)

        for _ in range(V2_SIGNATURE_ROUNDS):
            snapshot = self.contour_signature

            def canonical(item: Any) -> Any:
                got = snapshot.get(item)
                if got is None:
                    return item
                return (item[0], "sig", got)

            scratch: dict[tuple["python.Class", int], int] = {}
            for binding in subjects:
                held = contents.get(binding)
                if held is not None:
                    # normalise the variable set. contour_variables returns
                    # whichever nodes the network happens to have built for
                    # this contour, and that differs between contours of one
                    # class, so two contours holding nothing can still get
                    # different signatures purely from one having a
                    # __getitem__ node and the other not. A signature has to
                    # depend on contents alone.
                    held = {
                        name: held.get(name, set())
                        for name in getattr(binding[0], "vars", {})
                        if name not in CONTOUR_SIGNATURE_SKIP
                    }
                if held is None:
                    # a contour minted since the sweep ran holds nothing yet.
                    # It still needs a signature, and the right one is the
                    # empty signature for its class, so that it interns
                    # together with every other empty contour of that class
                    # instead of standing as its own raw identity in every
                    # cart that mentions it.
                    held = empty_contents(binding[0])
                signature = contour_signature(held, canonical)
                scratch[binding] = self.signature_id(binding[0], signature)
            if scratch == snapshot:
                break
            self.contour_signature = scratch

        changed = [
            binding
            for binding in subjects
            if binding in previous
            and previous[binding] != self.contour_signature.get(binding)
        ]
        if os.environ.get("SS_V2_UPGRADES"):
            by_id = {v: k for k, v in self.signature_ids.items()}
            for binding in changed[:12]:
                was = by_id.get(previous[binding], (None, ()))[1]
                now = by_id.get(self.contour_signature[binding], (None, ()))[1]
                logger.debug(
                    "    upgrade %s(%d): %s  ->  %s",
                    binding[0].ident,
                    binding[1],
                    render_signature(was),
                    render_signature(now),
                )
            if len(changed) > 12:
                logger.debug("    ... %d more upgrade(s)", len(changed) - 12)
        self.upgrades = len(changed)
        return len(changed)

    # --- stage 4: in-function sites, discovered as their templates appear

    def note_mold(
        self, gx: "config.GlobalInfo", alloc_id: Any, node: infer.CNode
    ) -> Optional[tuple["python.Class", int]]:
        """Serve the contour of a known site; only record an unknown one.

        Called from `ifa_seed_template` at the moment a template is created.
        A site the core has a contour for — committed, or minted at the end
        of the previous round — is given it. A site the core has never seen
        is written down and nothing else; it gets whatever the existing
        machinery would have given it, which under the freeze is an inert
        contour that cannot receive anything.

        Not minting here is the point. Minting during propagation feeds
        itself: the new contour enters an argument product, the product keys
        a template, the template asks for another contour, and round it
        goes, with nothing settled and so no way to notice the contours are
        all the same shape. Deferring the mint to the end of the round
        breaks that inside a propagation, and re-deriving the keys from
        settled signatures keeps the next round from building products out
        of distinctions that do not exist.
        """
        key = self.canonical_key(alloc_id)
        self.raw_ids.setdefault(key, alloc_id)
        binding = self.alloc_bindings.get(key)
        if binding is None:
            binding = self.provisional.get(key)
        if binding is not None:
            gx.alloc_info[alloc_id] = binding
            return binding

        types = gx.orig_types.get(node) or gx.types.get(node) or set()
        if len(types) != 1:
            # a constructor node should allocate exactly one class; if it does
            # not, this is not a site the core can describe
            return None
        cl, _dcpa = next(iter(types))
        if not isinstance(cl, python.Class):
            return None
        if allocation_site_kind(cl) != ALLOC_CONTAINER:
            # user classes get one contour each and are never split, scalars
            # never get one at all
            return None

        self.discovered[key] = cl
        self.misses += 1
        return None

    def mint_batch(
        self, limit: int
    ) -> list[tuple[Any, tuple["python.Class", int]]]:
        """Give contours to up to `limit` discovered sites.

        `limit` is unlimited by default (see V2_SITES_PER_ROUND). One is the
        safe schedule: a site is named by the signatures of the contours in
        its argument product, so naming it while those signatures are still
        moving gives it a name that will not mean the same thing next round.
        Adding several at once means each one shifts the signatures the
        others were named under.

        Minting more per round trades that guarantee for speed, since each
        round costs a full propagation to convergence. If the growth table
        still shows `found` falling to zero, the larger batch happened not
        to disturb anything and the answer is the same for far fewer rounds.
        If it churns instead — `found` refusing to settle, `upgrade` staying
        lively — set SS_V2_SITES_PER_ROUND=1.
        """
        added = []
        for key in sorted(self.discovered, key=canonical_key_sort):
            if len(added) >= limit:
                break
            if key in self.alloc_bindings or key in self.provisional:
                continue
            cl = self.discovered[key]
            contour = self.new_contour(cl)
            binding = (cl, contour)
            self.provisional[key] = binding
            added.append((key, binding))
        return added

    def mint_one(self) -> Optional[tuple[Any, tuple["python.Class", int]]]:
        """Give a contour to exactly one discovered site, and stop.

        One at a time, against a core that has settled. That is the
        condition the whole scheme rests on: a site is named by the
        signatures of the contours in its argument product, so naming it
        while those signatures are still moving gives it a name that will
        not mean the same thing next round. Minting a batch breaks it,
        because every contour in the batch shifts the signatures the rest of
        the batch was named under, and the site set churns instead of
        settling.

        The site chosen is the first in program order, so which one is added
        first is a property of the source rather than of dictionary
        iteration.
        """
        for key in sorted(self.discovered, key=canonical_key_sort):
            if key in self.alloc_bindings or key in self.provisional:
                continue
            cl = self.discovered[key]
            contour = self.new_contour(cl)
            binding = (cl, contour)
            self.provisional[key] = binding
            return key, binding
        return None

    def pending_count(self) -> int:
        """How many discovered sites are still waiting for a contour."""
        return sum(
            1
            for key in self.discovered
            if key not in self.alloc_bindings and key not in self.provisional
        )

    def owned_contours(self) -> set[tuple["python.Class", int]]:
        """Every contour any site owns, committed or provisional."""
        return (
            set(self.bindings.values())
            | set(self.alloc_bindings.values())
            | set(self.provisional.values())
        )

    def open_contours(self) -> set[tuple["python.Class", int]]:
        """Contours that may receive inflow: every site's own."""
        return self.owned_contours()

    def committed_contours(self) -> set[tuple["python.Class", int]]:
        """Every contour bound to a site."""
        return self.owned_contours()

    def learn(
        self, cl: "python.Class", contour: int, name: str, types: infer.Types
    ) -> infer.Types:
        """Add types to a contour variable; return the ones that were new."""
        key = (cl, contour, name)
        known = self.contents.setdefault(key, set())
        new = types - known
        known |= new
        return new

    def compact(self) -> None:
        """Reclaim contour numbers minted for provisionals that got merged.

        A provisional contour that merged into another was never committed,
        so its number was never a fact about anything and can be handed out
        again. Without this the numbering climbs by the number of sites
        discovered rather than the number kept, and cl.dcpa with it.
        """
        highest: dict["python.Class", int] = {}
        for cl, contour in self.committed_contours():
            highest[cl] = max(highest.get(cl, -1), contour)
        for cl in list(self.next_contour):
            baseline = self.baseline_dcpa.get(cl, 0)
            self.next_contour[cl] = max(baseline, highest.get(cl, -1) + 1)


def apply_core(
    gx: "config.GlobalInfo",
    core: FrozenCore,
    baseline_dcpa: dict["python.Class", int],
) -> None:
    """Rebuild the committed contours on top of a freshly restored network.

    Module-level sites have their contour written straight onto their
    constructor node. In-function sites cannot: the node they allocate at
    does not exist until its template does. Their contours go into
    gx.alloc_info instead, keyed exactly as ifa_seed_template will look them
    up, so that when the template is created the site is given the contour
    the core already committed to rather than a fresh one.
    """
    for cl, dcpa in baseline_dcpa.items():
        cl.dcpa = dcpa
    for cl, nxt in core.next_contour.items():
        cl.dcpa = max(cl.dcpa, nxt)

    for cl, contour in core.committed_contours():
        infer.class_copy(gx, cl, contour)

    for binding in set(core.provisional.values()):
        # a round's provisional contours are carried across its sweeps, so
        # that repeating a sweep re-reads the same contours instead of
        # minting a parallel set of them each time
        infer.class_copy(gx, binding[0], binding[1])
        binding[0].dcpa = max(binding[0].dcpa, binding[1] + 1)

    for cnode_thing, (cl, contour) in core.bindings.items():
        cnode = gx.cnode.get((cnode_thing, 0, 0))
        if cnode is not None:
            gx.types[cnode] = {(cl, contour)}

    for alloc_id, binding in core.alloc_bindings.items():
        gx.alloc_info[alloc_id] = binding

    for alloc_id, binding in core.provisional.items():
        gx.alloc_info[alloc_id] = binding

    # Contents are deliberately not seeded back. They are an *observation* of
    # a world that is still being built: while sites are still being
    # discovered, an unbound site allocates into a shared gx.list_types
    # bucket, and a contour observed in that round can pick up a type that
    # belongs to somebody else. Accumulating those observations makes the
    # mistake permanent — on amaze, readFile's `lines` was observed once, in
    # the round after it was bound, holding int as well as str, and no later
    # round could take it back. Each sweep re-derives contents from the
    # constraints instead, so what the core holds is always what the current
    # set of bindings actually implies.


CONTOUR_SIGNATURE_SKIP = frozenset(["__class__"])


def contour_signature(
    contents: dict[str, infer.Types],
    canonical: Optional[Any] = None,
) -> tuple:
    """A canonical rendering of what one contour holds.

    This is the thing pre-merging compares. Two contours of the same class
    with equal signatures hold the same types in the same variables, so a
    site pointing at one would see exactly what it sees pointing at the
    other; keeping both is what lets contour identity multiply without any
    type getting deeper.

    `remap` rewrites contours that are themselves being merged, so that a
    list of tuple2(5) and a list of tuple2(7) compare equal once tuple2(5)
    and tuple2(7) have been found equal.

    The contents are the ones recorded while the sweep's network was still
    live. Reading them back off gx afterwards would see a restored network
    in which none of these contours exist, and every signature would compare
    equal-and-empty.
    """
    parts = []
    for name in sorted(contents):
        if name in CONTOUR_SIGNATURE_SKIP:
            continue
        types = contents[name]
        if canonical is not None:
            # in terms of signatures, not contour numbers: two contours that
            # hold the same thing have to look the same here, or nothing
            # that contains them ever settles
            types = {canonical(item) for item in types}
        parts.append((name, frozenset(types)))
    return tuple(parts)


def signature_is_empty(signature: tuple) -> bool:
    """Whether a signature says nothing: every variable still empty."""
    return all(not types for _name, types in signature)


class RoundStats(NamedTuple):
    """What one outer round of stage 4 did.

    `discovered` is how many in-function sites the round found that the core
    had never seen. `merged` is how many of those turned out to have the
    signature of a contour that already existed, and `minted` how many got a
    contour of their own. `learned` counts sites whose contour gained a type
    it did not have before. A round that discovers nothing and learns nothing
    is the fixpoint.

    `upgrades` is how many contours moved to a larger signature this round,
    which is how a site whose contour was empty comes to be looked up under
    a bigger key. `signatures` is how many distinct signatures exist, which
    is the quantity the number of keys — and so the number of sites — is
    bounded by. Both flattening is convergence.
    """

    round: int
    sweeps: int
    discovered: int
    merged: int
    minted: int
    learned: int
    templates: int
    contours: int
    upgrades: int
    signatures: int


class CommitResult(NamedTuple):
    """What committing one round added to the core.

    `probe_fresh` and `mold_fresh` are the types that were genuinely new to
    the core, not everything the sweep saw. A round that re-observes what it
    already knew has learned nothing, and reporting it as learning would hide
    the very thing the round loop is watching for.
    """

    bound: dict[Any, tuple["python.Class", int]]
    merged: int
    minted: int
    probe_fresh: dict[AllocationSite, dict[str, infer.Types]]
    mold_fresh: dict[Any, dict[str, infer.Types]]

    @property
    def learned(self) -> int:
        return len(self.probe_fresh) + len(self.mold_fresh)


def commit_round(
    gx: "config.GlobalInfo",
    core: FrozenCore,
    result: "SweepResult",
) -> CommitResult:
    """Turn one settled round into committed facts.

    What is committed: the contents each contour was learned to hold, and
    the promotion of the round's provisional bindings to real ones. No
    contour is merged into any other, so no site's inflow is ever mixed with
    another's; sites that hold the same thing are brought together by the
    key they are looked up under, not by sharing a contour.
    """
    probe_fresh: dict[AllocationSite, dict[str, infer.Types]] = {}
    for site, inflow in result.probe_inflow.items():
        cl, contour = core.bindings[site.node]
        fresh = {}
        for name, types in inflow.items():
            new = core.learn(cl, contour, name, types)
            if new:
                fresh[name] = new
        if fresh:
            probe_fresh[site] = fresh

    # what every contour was observed to hold this round, replacing what it
    # was observed to hold last round
    observed: dict[tuple["python.Class", int, str], infer.Types] = {}
    for (cl, contour), held in result.contour_contents.items():
        for name, types in held.items():
            if types:
                observed[(cl, contour, name)] = set(types)

    bound: dict[Any, tuple["python.Class", int]] = {}
    for key, binding in core.provisional.items():
        core.alloc_bindings[key] = binding
        bound[key] = binding

    mold_fresh: dict[Any, dict[str, infer.Types]] = {}
    for key, inflow in result.mold_inflow.items():
        binding = core.alloc_bindings.get(key)
        if binding is None:
            continue
        cl, contour = binding
        fresh = {}
        for name, types in inflow.items():
            new = core.learn(cl, contour, name, types)
            if new:
                fresh[name] = new
        if fresh:
            mold_fresh[key] = fresh

    core.provisional = {}
    core.contents = observed
    return CommitResult(bound, 0, len(bound), probe_fresh, mold_fresh)


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
    # cpa numbering depends on the order templates happened to be created,
    # so it is not a stable tiebreak; the argument signature is a property of
    # the program and is
    records.sort(key=lambda r: (r.builtin, r.name(), r.dcpa, repr_cart(r.cart)))
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


class SweepResult(NamedTuple):
    """What one sweep saw, before any of it is committed.

    None of this is a fact yet. `probe_inflow` and `mold_inflow` are what
    arrived in each open contour during this sweep, and `provisional` is the
    set of sites the sweep discovered and minted contours for. They become
    facts in commit_round, once the sweep has stopped changing.
    """

    probe_inflow: dict[AllocationSite, dict[str, infer.Types]]
    mold_inflow: dict[Any, dict[str, infer.Types]]
    contour_contents: dict[
        tuple["python.Class", int], dict[str, infer.Types]
    ]
    provisional: dict[Any, tuple["python.Class", int]]
    rounds: int
    unreached: int
    templates: list[TemplateRecord]


def sweep_once(
    gx: "config.GlobalInfo",
    probes: list[AllocationSite],
    core: FrozenCore,
    baseline_dcpa: dict["python.Class", int],
    probes_and_molds: Optional[list[AllocationSite]] = None,
    collect: bool = False,
    freeze: bool = True,
    discover: bool = True,
) -> SweepResult:
    """One propagation with every bound contour open; read them all.

    Each site owns a contour nothing else uses, so what lands in a contour is
    attributable to its site whether one site is open or all of them are.
    Opening them together means one propagation per sweep instead of one per
    site, and it costs nothing in attribution.

    With `discover` on, a mold whose template is created during this
    propagation becomes a site and is minted a contour of its own on the
    spot (see FrozenCore.mold_contour). That contour is provisional: it is
    open for the rest of the sweep so that what flows into it is
    attributable, but it is not a binding until the caller commits it. A
    sweep never commits anything; that is what keeps a merge from being
    decided against a signature that has not settled.
    """
    saved_dcpa = dict(baseline_dcpa)
    saved_alloc_info = gx.alloc_info.copy()
    saved_orig_types = gx.orig_types
    backup = infer.backup_network(gx)

    core.open_set = None
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
    seeded_molds = {}
    for alloc_id, (cl, contour) in list(core.alloc_bindings.items()) + list(
        core.provisional.items()
    ):
        seeded_molds[alloc_id] = {
            name: node.types().copy()
            for name, node in contour_variables(gx, cl, contour).items()
        }

    # Freezing keeps sites that do not own a contour from merging into each
    # other through the shape-keyed buckets in gx.list_types, which is what
    # a sweep needs. It applies to contour-carrying classes only; freezing
    # user class attributes as well would starve template creation and so
    # stop the sweep from discovering any new sites at all.
    open_set = core.open_contours() if freeze else None
    if open_set is not None:
        # contours minted by an earlier sweep of this round are still
        # provisional, but they exist and have to stay readable
        open_set |= set(core.provisional.values())
    core.open_set = open_set
    gx.infer_v2_open_contours = open_set
    gx.infer_v2_core = core if discover else None
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

        mold_results: dict[Any, dict[str, infer.Types]] = {}
        every_mold = dict(core.alloc_bindings)
        every_mold.update(core.provisional)
        every_mold.update(
            {k: v for k, v in core.provisional.items()}
        )
        for alloc_id, (cl, contour) in every_mold.items():
            inflow = {}
            before = seeded_molds.get(alloc_id, {})
            for name, node in contour_variables(gx, cl, contour).items():
                arrived = node.types() - before.get(name, set())
                if arrived:
                    inflow[name] = arrived
            if inflow:
                mold_results[alloc_id] = inflow

        provisional = dict(core.provisional)

        # what every contour in play holds, read while the network is still
        # up. This is what pre-merging compares signatures on; after the
        # restore below none of these contours exist any more.
        contour_contents: dict[
            tuple["python.Class", int], dict[str, infer.Types]
        ] = {}
        frontier = set(core.owned_contours())
        for _ in range(V2_SIGNATURE_ROUNDS):
            if not frontier:
                break
            following: set[tuple["python.Class", int]] = set()
            for binding in frontier:
                if binding in contour_contents:
                    continue
                held = {
                    name: node.types().copy()
                    for name, node in contour_variables(
                        gx, binding[0], binding[1]
                    ).items()
                }
                contour_contents[binding] = held
                for types in held.values():
                    for item in types:
                        # a contour nobody owns still holds something, and a
                        # list containing it has to be able to say what. Left
                        # out, it stays a raw contour number in every
                        # signature that mentions it, so a list holding the
                        # mold tuple never looks like a list holding an
                        # identical site tuple, and the two never intern to
                        # one signature.
                        if item in contour_contents:
                            continue
                        if not isinstance(item[0], python.Class):
                            continue
                        if allocation_site_kind(item[0]) != ALLOC_CONTAINER:
                            continue
                        following.add(item)
            frontier = following

        templates = collect_templates(gx, probes_and_molds) if collect else []
    finally:
        gx.infer_v2_open_contours = None
        gx.infer_v2_core = None
        core.open_set = None
        infer.restore_network(gx, backup)
        gx.alloc_info = saved_alloc_info
        gx.orig_types = saved_orig_types
        for klass, dcpa in saved_dcpa.items():
            klass.dcpa = dcpa

    return SweepResult(
        results,
        mold_results,
        contour_contents,
        provisional,
        rounds,
        unreached,
        templates,
    )


def sweep_to_convergence(
    gx: "config.GlobalInfo",
    probes: list[AllocationSite],
    core: FrozenCore,
    baseline_dcpa: dict["python.Class", int],
    sites: list[AllocationSite],
    round_no: int,
    collect: bool,
) -> tuple[SweepResult, int]:
    """Sweep until a whole sweep learns nothing, then return the last one.

    Nothing is committed here. A sweep is repeated because a site whose
    contents only arrive through some object's attribute cannot learn
    anything until that attribute has been populated by another site, so one
    sweep is not enough to settle the round; and it is the settled state, not
    any intermediate one, that the caller is allowed to commit.

    The repeated sweeps re-derive the same provisional bindings each time,
    because each starts from the same committed core and propagation is
    deterministic. What changes between them is only how much has arrived.
    """
    last: Optional[SweepResult] = None
    sweep = 0
    seen: dict[tuple[Any, str], infer.Types] = {}
    while sweep < V2_MAX_SWEEPS:
        sweep += 1
        result = sweep_once(
            gx,
            probes,
            core,
            baseline_dcpa,
            probes_and_molds=sites,
            collect=collect,
        )
        last = result

        # a sweep has settled when it saw nothing it had not seen before;
        # this compares against the previous sweep of the same round rather
        # than against the core, because the core has not been told any of
        # this yet
        fresh = 0
        for site, inflow in result.probe_inflow.items():
            for name, types in inflow.items():
                key = (site.node, name)
                if types - seen.get(key, set()):
                    seen.setdefault(key, set()).update(types)
                    fresh += 1
        for alloc_id, inflow in result.mold_inflow.items():
            for name, types in inflow.items():
                key = (alloc_id, name)
                if types - seen.get(key, set()):
                    seen.setdefault(key, set()).update(types)
                    fresh += 1

        logger.debug(
            "  round %d sweep %d: %d contour variable(s) grew,"
            " %d provisional site(s)%s (%d propagation round(s))",
            round_no,
            sweep,
            fresh,
            len(result.provisional),
            ", %d not reached" % result.unreached if result.unreached else "",
            result.rounds,
        )
        if not fresh:
            break
    else:
        logger.warning(
            "infer v2: round %d stopped after %d sweeps without settling",
            round_no,
            V2_MAX_SWEEPS,
        )

    assert last is not None
    return last, sweep


def report_round_learning(
    core: FrozenCore,
    commit: CommitResult,
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
            if name in CONTOUR_SIGNATURE_SKIP:
                continue
            logger.debug("      %-8s <- %s", name, format_types(fresh[name]))


def alloc_id_source(alloc_id: Any) -> str:
    """Render the AST node of an alloc_id as source, for logging."""
    node = alloc_id[2]
    try:
        text = " ".join(ast.unparse(node).split())
    except Exception:  # pragma: no cover - defensive
        return "<%s>" % type(node).__name__
    if len(text) > ALLOC_SOURCE_MAXLEN:
        text = text[: ALLOC_SOURCE_MAXLEN - 3] + "..."
    return text


def alloc_id_location(alloc_id: Any) -> str:
    """Render 'function:line' for an alloc_id, for logging."""
    node = alloc_id[2]
    lineno = getattr(node, "lineno", None)
    return "%s:%s" % (alloc_id[0], lineno if lineno is not None else "-")


def report_new_sites(
    result: "SweepResult",
    commit: CommitResult,
    round_no: int,
) -> None:
    """Log the in-function sites this round discovered and what they hold.

    A site whose provisional contour merged into another is shown with the
    number it was minted as, so the listing says which decision was made
    rather than only its outcome.
    """
    bound = commit.bound
    if not bound:
        return
    logger.debug(
        "  round %d: %d new in-function allocation site(s)", round_no, len(bound)
    )
    shown = 0
    for alloc_id in sorted(bound, key=alloc_id_location):
        if shown >= V2_MAX_SITE_LINES:
            logger.debug(
                "  ... %d more new site(s) not listed", len(bound) - shown
            )
            break
        shown += 1
        cl, contour = bound[alloc_id]
        provisional = result.provisional.get(alloc_id)
        note = ""
        if provisional is not None and provisional != (cl, contour):
            note = "  (merged from %d)" % provisional[1]
        logger.debug(
            "    %-24s %-10s contour %-4d %s%s",
            alloc_id_location(alloc_id),
            cl.ident,
            contour,
            alloc_id_source(alloc_id),
            note,
        )
        inflow = result.mold_inflow.get(alloc_id, {})
        for name in sorted(inflow):
            if name in CONTOUR_SIGNATURE_SKIP:
                continue
            logger.debug("        %-8s <- %s", name, format_types(inflow[name]))


def report_widest_signatures(core: FrozenCore, round_no: int) -> None:
    """Log which functions own the most contours, and how many keys exist.

    This is the per-site contour count. If a function's contour count keeps
    climbing round on round while its signature count does not, contours are
    multiplying without holding anything new, which is the shape a runaway
    would have.
    """
    per_function: dict[str, int] = {}
    for key in core.alloc_bindings:
        per_function[key[0]] = per_function.get(key[0], 0) + 1
    if not per_function:
        return
    widest = sorted(per_function.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    if widest[0][1] < 2:
        return
    logger.debug("  round %d: functions owning the most sites:", round_no)
    for function, count in widest:
        logger.debug("    %-32s %d site(s)", function, count)


def report_added_site(
    core: FrozenCore,
    added: tuple[Any, tuple["python.Class", int]],
    round_no: int,
    pending: int,
) -> None:
    """Log the single site this round gave a contour to."""
    key, (cl, contour) = added
    logger.debug(
        "  round %d: +1 site %s  %s  contour %d  (%d still waiting)",
        round_no,
        alloc_id_location(key),
        cl.ident,
        contour,
        pending - 1,
    )
    logger.debug("      %s   cart %s", alloc_id_source(key), repr_cart(key[1]))


def report_round(stats: RoundStats) -> None:
    """One line summarising a round, and the numbers a hang would show in."""
    logger.debug(
        "[infer v2: round %d done: %d sweep(s), %d site(s) discovered"
        " (%d merged, %d minted), %d learned, %d template(s),"
        " %d contour(s) total]",
        stats.round,
        stats.sweeps,
        stats.discovered,
        stats.merged,
        stats.minted,
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
    without the discovered count falling off. Convergence shows up as both
    flattening and the last round discovering nothing.
    """
    logger.debug("[infer v2: growth per round]")
    logger.debug(
        "    %-6s %-7s %-7s %-7s %-8s %-9s %-10s %-7s %-5s",
        "round",
        "sweeps",
        "found",
        "merged",
        "learned",
        "contours",
        "templates",
        "upgrade",
        "sigs",
    )
    for stats in history:
        logger.debug(
            "    %-6d %-7d %-7d %-7d %-8d %-9d %-10d %-7d %-5d",
            stats.round,
            stats.sweeps,
            stats.discovered,
            stats.merged,
            stats.learned,
            stats.contours,
            stats.templates,
            stats.upgrades,
            stats.signatures,
        )


def probe_allocation_sites(
    gx: "config.GlobalInfo", sites: list[AllocationSite]
) -> FrozenCore:
    """Accumulate a frozen core over rounds, until a round adds nothing.

    A round is: sweep until the sweeps stop learning, then commit everything
    that settled — the contents of the contours, the bindings of the sites
    discovered along the way, and the merges of the ones whose signatures
    turned out to agree. Commit happens once, at the end, for all of it
    together, because bindings and contents are trustworthy for the same
    reason and no earlier.

    Module-level sites are bound before the first sweep rather than when they
    first learn something. Otherwise a site swept early sees its neighbours
    still sitting in their shape-keyed default contours and records that as a
    fact, and the core is append-only, so a contour learned before its owner
    was bound can never be taken back.

    In-function sites cannot be bound up front, because they do not exist
    until their templates do. They are discovered during a sweep and minted
    provisional contours there; the provisional contours are scratch for the
    duration of that sweep and become bindings only at the commit.

    Rounds repeat because the site set grows: new sites feed argument
    products, products key new templates, and templates hold more molds. That
    is the feedback loop, and it is the reason this loop — unlike the sweep
    loop inside it — is not guaranteed to be short.
    """
    containers = [site for site in sites if site.kind == ALLOC_CONTAINER]
    probes = [site for site in containers if site.module_level]
    molds = len(containers) - len(probes)
    logger.debug(
        "[infer v2: %d module-level container site(s);"
        " %d in-function mold(s) to be discovered per template]",
        len(probes),
        molds,
    )

    core = FrozenCore()
    # Never mint below 2. A class whose dcpa is 1 has no contour 1 nodes,
    # because analyze() only class_copies range(1, dcpa) — but the graph
    # still types every mold constructor of that class as contour 1. Minting
    # contour 1 for a site gives that contour real variable nodes, and every
    # mold in the builtins starts flowing into it: dict.items' tuple2, zip's
    # tuple, and so on, straight into a user variable. Leaving contour 1
    # node-less keeps the molds inert, which is what they are for.
    baseline_dcpa = {cl: max(cl.dcpa, 2) for cl in gx.allclasses}
    core.baseline_dcpa = dict(baseline_dcpa)
    for site in probes:
        core.contour_for(site, baseline_dcpa)

    history: list[RoundStats] = []
    round_no = 0
    last_templates: list[TemplateRecord] = []
    while round_no < V2_MAX_ROUNDS:
        round_no += 1
        logger.debug("[infer v2: round %d]", round_no)

        result, sweeps = sweep_to_convergence(
            gx, probes, core, baseline_dcpa, sites, round_no, collect=True
        )

        # commit what settled, then re-derive every contour's signature from
        # it. Only now, with nothing in flight and every signature settled,
        # is a name for a new site meaningful.
        commit = commit_round(gx, core, result)
        pending = core.pending_count()
        batch = core.mint_batch(V2_SITES_PER_ROUND)
        added = batch[0] if batch else None
        # after the mint, never before: a contour with no signature falls
        # back to its own number in every cart that mentions it, which is a
        # distinction the next round would mint yet another contour for
        upgrades = core.resignature(result.contour_contents)
        # signatures just moved, so the names built from them have moved too
        core.rekey()

        report_round_learning(core, commit, round_no)
        for entry in batch:
            report_added_site(core, entry, round_no, pending)
        if result.templates:
            last_templates = result.templates

        stats = RoundStats(
            round=round_no,
            sweeps=sweeps,
            discovered=len(batch),
            merged=0,
            minted=pending,
            learned=commit.learned,
            templates=len(result.templates),
            contours=len(core.owned_contours()),
            upgrades=upgrades,
            signatures=len(core.signature_ids),
        )
        history.append(stats)
        report_round(stats)

        if not batch and not commit.learned and not upgrades:
            break
    else:
        logger.warning(
            "infer v2: stopped after %d rounds without converging;"
            " see the growth table for whether it was still climbing",
            V2_MAX_ROUNDS,
        )

    report_growth(history)
    report_core(core, round_no)
    report_templates(last_templates)
    return core


def report_signature_table(core: FrozenCore) -> None:
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


def report_site_signatures(gx: "config.GlobalInfo", core: FrozenCore) -> None:
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


def report_core(core: FrozenCore, rounds: int) -> None:
    report_signature_table(core)
    """Summarise what the rounds established."""
    logger.debug(
        "[infer v2: frozen core after %d round(s): %d module-level site(s),"
        " %d in-function site(s), %d contour(s), %d contour variable(s)]",
        rounds,
        len(core.bindings),
        len(core.alloc_bindings),
        len(core.committed_contours()),
        len(core.contents),
    )
    per_class: dict[str, int] = {}
    for cl, _contour in core.committed_contours():
        per_class[cl.ident] = per_class.get(cl.ident, 0) + 1
    for ident in sorted(per_class):
        logger.debug("    %-10s %d contour(s)", ident, per_class[ident])


def infer_v2_analysis(gx: "config.GlobalInfo") -> None:
    """Experimental alternative entry point to iterative_dataflow_analysis.

    Stage 1: inventory the constructor nodes, separating module-level
        allocation sites from in-function molds.
    Stage 2: sweep the module-level sites, each owning a contour of its own,
        committing what flows in to an append-only core until a whole sweep
        learns nothing.
    Stage 3: keep the templates each sweep creates, so the molds that become
        allocation sites inside them can be seen.
    Stage 4: let those molds become sites. A mold is given a contour when its
        template is created, learns over the round's sweeps, and is committed
        at the end of the round — reusing a contour whose settled signature
        it matches, or keeping its own. Rounds repeat until one adds nothing.

    There is no stage that infers enough to generate code, so this stops here
    rather than falling back to the existing analysis. Run without --infer-v2
    to compile.
    """
    logger.info("[analyzing types..]")
    all_sites = collect_allocation_sites(gx, builtins=True)
    # Module-level allocations in builtin modules — sys.argv and friends —
    # are real sites too. They are few, and excluding them leaves them on a
    # shared bucket contour that the freeze keeps empty, so `for arg in
    # sys.argv` yields nothing and arg "has no type". This is only about
    # module-level ones: builtin *molds* must stay out, since builtin methods
    # are analysed through them.
    sites = [
        site
        for site in all_sites
        if not site.builtin or site.module_level
    ]
    builtin_count = len(all_sites) - len(sites)
    report_allocation_sites(gx, sites, builtin_count)
    core = probe_allocation_sites(gx, sites)
    report_site_signatures(gx, core)

    if not gx.infer_v2_codegen:
        logger.debug("[infer v2: stopping after inspection; no C++ is generated]")
        sys.exit(0)

    materialize(gx, core)


def materialize(gx: "config.GlobalInfo", core: FrozenCore) -> None:
    """Leave the analyzed network standing, for code generation.

    Every sweep restores the network when it is done, so once the rounds
    finish the analysis exists only in the core and gx is back at its
    pristine state. Code generation reads gx.types and func.cp, so the
    result has to be put back: apply the core, propagate once with nothing
    frozen, and this time do not restore.

    Frozen, with every committed contour open. The freeze exists to keep
    sites that do not own a contour from merging into each other, and by now
    every site the rounds found does own one, so the open set is everything
    that matters and the freeze dissolves on its own — which is what §4.3 of
    the design notes predicted.

    Propagating unfrozen here instead throws the whole analysis away. The
    rounds run frozen, so their cartesian products are built from the
    contours the core owns; an unfrozen pass produces different products,
    every site's canonical key misses, and every one of them falls back to
    the mother-contour heuristic. Measured on test_prog_nqueens: 12 of 12
    sites missed, and the generated C++ widened to list<pyseq<int>*> where
    the unpatched compiler gives list<list<int>*>.
    """
    baseline_dcpa = {cl: cl.dcpa for cl in gx.allclasses}
    apply_core(gx, core, baseline_dcpa)
    gx.orig_types = {node: types.copy() for node, types in gx.types.items()}
    gx.infer_v2_open_contours = core.open_contours()
    core.open_set = gx.infer_v2_open_contours
    gx.infer_v2_core = core
    core.misses = 0
    try:
        rounds = v2_propagate(gx)
    finally:
        gx.infer_v2_core = None
        gx.infer_v2_open_contours = None
        core.open_set = None
    logger.debug(
        "[infer v2: materialised in %d propagation round(s); %d contour(s);"
        " %d site(s) fell back to the old heuristic]",
        rounds,
        len(core.owned_contours()),
        core.misses,
    )
