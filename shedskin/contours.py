# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.contours: deciding which container contours exist

`shedskin.infer` builds the constraint graph and propagates types through it,
with CPA (the cartesian product algorithm) copying each function into one
*template* per combination of argument types. That takes care of polymorphic
functions. This module takes care of polymorphic *containers*: it decides how
many distinct list (dict, tuple, ...) types the program needs, and which
allocations share one.

Each distinct container type is a *contour* of its class: (list, 7) and
(list, 9) are two list types, say list[int] and list[str]. User classes are not
split; scalars have no contours.

The model
---------

An allocation written at module level is one site, and simply gets a contour
of its own.

An allocation written inside a function (a *mold*) becomes one site per
template of that function. Such a site is identified by its *product*:
(function, argument types of the template, AST node). The argument types
mention contours, so products are as fine-grained as the contours are.

To decide sharing, each product also has a *name*: the product with every
container contour in it replaced by that contour's *signature*, a canonical
description of what the contour holds (list of int, dict of str to list of
int, ...). Products with the same name share one contour; products with
different names get different contours. So a list allocated in f(list[int])
and one allocated in f(list[str]) are kept apart, while the endless chain of
templates a recursive f(list[int]) would otherwise create collapses into one.

The rounds
----------

Names depend on signatures, signatures on what flows into contours, and that
on which contours exist. So the analysis iterates. The state carried between
rounds is the *core* (`FrozenCore`): which product owns which contour, the
signature of every contour, and the name index derived from those two. Each
round:

  1. sweep: restore the pristine graph, give every known site its contour,
     and propagate. Container contours that no site owns are *frozen*: they
     may flow, but receive nothing, so they cannot mix up the types of sites
     that have not been given a contour yet.
  2. observe what each contour holds, and recompute all signatures from
     that, innermost containers first.
  3. rekey: rebuild the name index from the owners under the new signatures.
  4. mint: every product found during the sweep that owns nothing and whose
     name is not in the index gets a new contour.

When a round mints nothing, defers nothing and changes no signature, the next
sweep would see exactly what this one saw, and the analysis is done. A final
propagation (`materialize`) then leaves the graph standing for code
generation.

The points that are easy to get wrong
-------------------------------------

- A product keeps the contour it was minted forever (`owners`); only its name
  moves as signatures change. Re-keying a binding by name instead strands
  contours (empty, but still served under a stale name), and dropping it
  makes sites be rediscovered without end.
- Contents are observed afresh every round, not accumulated: a type seen
  while other sites were still unbound may be wrong, and must be allowed to
  disappear again. As a consequence signatures can move both ways.
- Minting happens between rounds, never during a sweep: a contour minted
  mid-propagation feeds new products, which mint more contours, before
  anything has settled enough to notice they hold the same thing.
- Some products are not real sites yet and wait: one keyed on a frozen
  (unowned) contour (`mentions_bucket`), and one keyed on a contour minted
  in the previous round, whose signature still says "empty" only because
  nothing has flowed into it yet (`mentions_fresh`).

There is no proof that the rounds always reach a fixpoint (signatures may
move down as well as up), but in practice they converge in a few dozen rounds
at most. Recursive container types (`l.append(l)`) are not supported.

Debugging: `-d3` logs each round, the growth table and the final signature
per site (see `shedskin.contours_report`); SS_CONTOUR_UPGRADES=1 shows how
signatures change, SS_CONTOUR_SIGDUMP=1 lists all signatures, and SS_CONTOUR_ROUNDS
caps the number of rounds. The last -d3 line should report 0 sites left
without a contour of their own: such a site keeps a frozen contour, and
whatever it holds is missing from the result.
"""

import os
import logging
from typing import TYPE_CHECKING, Any, NamedTuple, Optional

from . import infer, contours_report, python

if TYPE_CHECKING:
    from . import config

logger = logging.getLogger("infer")


# cartesian product limit while propagating
CPA_LIMIT = 1000

# safety bound on the number of rounds; real programs need a few dozen
MAX_ROUNDS = int(os.environ.get("SS_CONTOUR_ROUNDS", 20000))

# bound on the signature fixpoint, i.e. on container nesting depth
SIGNATURE_ROUNDS = 12


class AllocationSite:
    """A constructor node: an AST expression that creates an object.

    At module level this is an allocation site. Inside a function it is a
    mold: the sites are its copies in each template of the function.
    """

    __slots__ = ("cnode", "cl", "dcpa", "parent", "module")

    def __init__(self, cnode: infer.CNode, cl: "python.Class", dcpa: int) -> None:
        self.cnode = cnode
        self.cl = cl
        self.dcpa = dcpa
        self.parent = cnode.parent
        self.module = cnode.mv.module

    @property
    def node(self) -> Any:
        """The AST node that allocates."""
        return self.cnode.thing

    @property
    def module_level(self) -> bool:
        """Whether this node is a site already, rather than a mold.

        A comprehension is compiled as a function, but one written at module
        level runs once and is never templated, so it counts as module level
        (python.outer_func skips comprehensions for the same reason).
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


def is_container(cl: Any) -> bool:
    """Whether a class is a builtin container, which is split into contours."""
    return (
        isinstance(cl, python.Class)
        and cl.mv.module.builtin
        and cl.ident in infer.SPLIT_CLASS_IDENTS
    )


def collect_allocation_sites(gx: "config.GlobalInfo") -> list[AllocationSite]:
    """Collect the constructor nodes of the program, at (node, 0, 0).

    Sorted, so that two runs over the same program see the same order.
    """
    sites = []
    for (_thing, dcpa, cpa), cnode in gx.cnode.items():
        if not cnode.constructor or dcpa != 0 or cpa != 0:
            continue
        types = gx.types.get(cnode, set())
        if len(types) != 1:
            continue  # a constructor node should allocate exactly one class
        cl, site_dcpa = next(iter(types))
        if isinstance(cl, python.Class):
            sites.append(AllocationSite(cnode, cl, site_dcpa))

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


def propagate(gx: "config.GlobalInfo") -> None:
    """Propagate to a fixpoint, with the cartesian product limit raised."""
    gx.cpa_limit = CPA_LIMIT
    gx.cpa_limited = False
    infer.propagate(gx)
    if gx.cpa_limited:
        logger.warning(
            "contours: a call has more than %d argument type combinations;"
            " its result types are incomplete",
            CPA_LIMIT,
        )


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


def render_item(item: Any) -> str:
    """Render one signature or cartesian product entry compactly."""
    if isinstance(item, tuple) and len(item) == 3 and item[1] == "sig":
        return "%s#%s" % (getattr(item[0], "ident", item[0]), item[2])
    if isinstance(item, tuple) and len(item) == 2:
        return "%s(%s)" % (getattr(item[0], "ident", item[0]), item[1])
    return str(item)


def canonical_key_sort(key: Any) -> tuple:
    """A deterministic order for products, based on the program text.

    Products hold AST nodes and classes, which would otherwise order by
    address and make the analysis order-dependent.
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
    return ",".join(render_item(item) for item in cart)


class FrozenCore:
    """The state carried from round to round.

    `bindings`: the contour of each module-level site, by AST node.
    `owners`: the contour of each in-function site, by product; only grows.
    `alloc_bindings`: the name index, name -> contour, derived from `owners`
        (see rekey).
    `contour_signature`: the signature id of each contour, interned through
        `signature_ids`.
    `discovered`: products seen during sweeps that had no contour; minted at
        the end of the round, unless their name is bound by then.
    `fresh_contours`: the contours minted at the end of the last round.
    """

    def __init__(self) -> None:
        self.bindings: dict[Any, tuple["python.Class", int]] = {}
        self.alloc_bindings: dict[Any, tuple["python.Class", int]] = {}
        self.next_contour: dict["python.Class", int] = {}
        self.baseline_dcpa: dict["python.Class", int] = {}
        self.discovered: dict[Any, "python.Class"] = {}
        self.signature_ids: dict[tuple[Any, tuple], int] = {}
        self.contour_signature: dict[tuple["python.Class", int], int] = {}
        self.owners: dict[Any, tuple["python.Class", int]] = {}
        self.fresh_contours: set[tuple["python.Class", int]] = set()
        # how many discovered products the last mint held back (mentions_fresh)
        self.deferred = 0
        # how many molds a propagation could not give a contour (for logging)
        self.misses = 0

    # --- contour allocation

    def new_contour(self, cl: "python.Class") -> int:
        """Mint an unused contour number for a class."""
        contour = self.next_contour.setdefault(
            cl, self.baseline_dcpa.get(cl, cl.dcpa)
        )
        self.next_contour[cl] = contour + 1
        return contour

    def bind_module_site(self, site: AllocationSite) -> None:
        """Give a module-level container site a contour of its own."""
        assert site.module_level, "only module-level sites own a contour here"
        assert is_container(site.cl), "only builtin containers are split"
        self.bindings[site.node] = (site.cl, self.new_contour(site.cl))

    # --- keys

    def signature_id(self, cl: "python.Class", signature: tuple) -> int:
        """Intern a settled signature, so equal ones get the same number."""
        key = (cl, signature)
        got = self.signature_ids.get(key)
        if got is None:
            got = len(self.signature_ids)
            self.signature_ids[key] = got
        return got

    def canonical_key(self, alloc_id: Any) -> Any:
        """The name of a product: its cartesian product in signature terms."""
        function, cart, node = alloc_id
        if isinstance(cart, tuple):
            sigs = self.contour_signature
            cart = tuple(in_signature_terms(item, sigs) for item in cart)
        return (function, cart, node)

    def rekey(self) -> None:
        """Rebuild the name index under the current signatures.

        Each owner is filed under its current name. When two owners now
        have the same name, the older one holds it; the younger one keeps
        its own contour, which note_mold still finds by product.
        """
        names: dict[Any, tuple["python.Class", int]] = {}
        for product, binding in self.owners.items():
            names.setdefault(self.canonical_key(product), binding)
        self.alloc_bindings = names

    def resignature(
        self,
        contents: dict[tuple["python.Class", int], dict[str, infer.Types]],
    ) -> int:
        """Recompute every contour's signature; return how many changed.

        A signature is written in terms of the signatures of what the
        contour holds, so a list of tuple2(11) and a list of tuple2(13) are
        the same when the two tuples hold the same thing. This is a fixpoint
        of its own, one pass per level of nesting. Each pass reads the
        previous pass's map and writes a new one; updating in place mixes
        the two and makes the ids depend on iteration order.
        """
        subjects = sorted(
            set(contents) | self.owned_contours(),
            key=lambda cc: (cc[0].ident, cc[1]),
        )
        previous = dict(self.contour_signature)

        for _ in range(SIGNATURE_ROUNDS):
            snapshot = self.contour_signature
            scratch: dict[tuple["python.Class", int], int] = {}
            for binding in subjects:
                signature = contour_signature(
                    binding[0], contents.get(binding) or {}, snapshot
                )
                scratch[binding] = self.signature_id(binding[0], signature)
            if scratch == snapshot:
                break
            self.contour_signature = scratch

        current = self.contour_signature
        changed = [
            binding
            for binding in previous.keys() | current.keys()
            if previous.get(binding) != current.get(binding)
        ]
        contours_report.report_upgrades(self, previous, changed)
        return len(changed)

    # --- sites in templates

    def note_mold(
        self, gx: "config.GlobalInfo", alloc_id: Any, node: infer.CNode
    ) -> Optional[tuple["python.Class", int]]:
        """The contour for a mold in a newly created template, if known.

        Called from infer.seed_template. A product is looked up by
        itself first (it owns a contour), then by name (it shares one).
        Otherwise it is only recorded in `discovered`, and keeps its class's
        frozen default contour for this sweep.
        """
        binding = self.owners.get(alloc_id)
        if binding is None:
            key = self.canonical_key(alloc_id)
            binding = self.alloc_bindings.get(key)
        if binding is not None:
            return binding

        types = gx.orig_types.get(node) or gx.types.get(node) or set()
        if len(types) != 1:
            return None
        cl, _dcpa = next(iter(types))
        if not is_container(cl):
            return None  # user classes are not split, scalars have no contours
        if self.mentions_bucket(alloc_id, node.parent):
            return None

        self.discovered[alloc_id] = cl
        self.misses += 1
        return None

    def mentions_bucket(self, product: Any, func: Any = None) -> bool:
        """Does a product mention a container contour nobody owns?

        Such a product belongs to a template that only exists because some
        site upstream has no contour yet, and which such templates appear
        depends on propagation order. It is skipped; once the upstream site
        is bound, the next round sees the real product.
        """
        cart = product[1]
        if not isinstance(cart, tuple):
            return False
        while isinstance(func, python.Function) and isinstance(
            func.parent, python.Function
        ):
            func = func.parent
        if (
            isinstance(func, python.Function)
            and isinstance(func.parent, python.Class)
            and func.ident in func.parent.staticmethods + func.parent.classmethods
        ):
            # the class itself leads the product of a static or class method;
            # it is not an allocated container
            cart = cart[1:]
        owned = None
        for item in cart:
            if not (isinstance(item, tuple) and len(item) == 2):
                continue
            if not is_container(item[0]):
                continue
            if owned is None:
                owned = self.owned_contours()
            if item not in owned:
                return True
        return False

    def mint_batch(self) -> list[tuple[Any, tuple["python.Class", int]]]:
        """Give a contour to every discovered product that needs one."""
        added = []
        self.deferred = 0
        for product in sorted(self.discovered, key=canonical_key_sort):
            if self.pending(product) is None:
                continue
            if self.mentions_fresh(product):
                self.deferred += 1
                continue
            added.append(self.mint(product))
        return added

    def pending(self, product: Any) -> Optional[Any]:
        """The name a discovered product would be minted under, or None if
        it owns a contour or its name is bound already.
        """
        if product in self.owners:
            return None
        fresh = self.canonical_key(product)
        if fresh in self.alloc_bindings:
            return None
        return fresh

    def mentions_fresh(self, product: Any) -> bool:
        """Does a product mention a contour minted last round?

        That contour's signature still says "empty" only because nothing
        flowed into it before it existed; a name built on it is premature.
        Waiting one round matters for a recursive function that creates a
        container and passes it to itself: otherwise every round mints one
        more site for the newest, still empty, container.
        """
        cart = product[1]
        if not self.fresh_contours or not isinstance(cart, tuple):
            return False
        return any(item in self.fresh_contours for item in cart)

    def mint(self, product: Any) -> tuple[Any, tuple["python.Class", int]]:
        """Give one discovered product a contour of its own."""
        fresh = self.canonical_key(product)
        cl = self.discovered[product]
        contour = self.new_contour(cl)
        binding = (cl, contour)
        self.alloc_bindings[fresh] = binding
        self.owners[product] = binding
        return fresh, binding

    def pending_count(self) -> int:
        """How many discovered products still wait for a contour."""
        return sum(
            1 for product in self.discovered if self.pending(product) is not None
        )

    def owned_contours(self) -> set[tuple["python.Class", int]]:
        """Every contour some site owns."""
        return set(self.bindings.values()) | set(self.owners.values())


def apply_core(
    gx: "config.GlobalInfo",
    core: FrozenCore,
    baseline_dcpa: dict["python.Class", int],
) -> None:
    """Recreate the core's contours on a freshly restored graph.

    Module-level sites get their contour on their constructor node. In-function
    sites get theirs when their template is created (see note_mold).
    """
    for cl, dcpa in baseline_dcpa.items():
        cl.dcpa = dcpa
    for cl, nxt in core.next_contour.items():
        cl.dcpa = max(cl.dcpa, nxt)

    for cl, contour in core.owned_contours():
        infer.class_copy(gx, cl, contour)

    for cnode_thing, (cl, contour) in core.bindings.items():
        cnode = gx.cnode.get((cnode_thing, 0, 0))
        if cnode is not None:
            gx.types[cnode] = {(cl, contour)}

    # contents are not seeded back: each sweep observes them afresh


def in_signature_terms(item: Any, signatures: dict[Any, int]) -> Any:
    """One type in signature terms: a contour with a signature becomes that
    signature; anything else (a user class instance, a scalar) stays as is."""
    got = signatures.get(item)
    if got is None:
        return item
    return (item[0], "sig", got)


def contour_signature(
    cl: "python.Class",
    held: dict[str, infer.Types],
    signatures: dict[Any, int],
) -> tuple:
    """What one contour of `cl` holds, with contours in signature terms.

    Every variable of the class is included, so that the result depends on
    the contents only, and not on which nodes the graph happens to have built
    for this contour; an empty contour gets the class's empty signature.
    """
    return tuple(
        (
            name,
            frozenset(in_signature_terms(t, signatures) for t in held.get(name, ())),
        )
        for name in sorted(cl.vars)
        if name != "__class__"
    )


class SweepResult(NamedTuple):
    """What one sweep saw. `templates` is only collected for -d3."""

    contour_contents: dict[
        tuple["python.Class", int], dict[str, infer.Types]
    ]
    templates: list["contours_report.TemplateRecord"]


def sweep(
    gx: "config.GlobalInfo",
    core: FrozenCore,
    pristine: infer.Backup,
    sites: list[AllocationSite],
) -> SweepResult:
    """Propagate once with every owned contour open, and read them all.

    Every site owns its own contour, so everything can be open at once
    without losing track of what flowed where. The graph is restored to
    `pristine` afterwards, so each sweep starts from the same state.
    """
    apply_core(gx, core, core.baseline_dcpa)

    # only container contours are frozen; freezing user class
    # attributes too would starve template creation
    gx.open_contours = core.owned_contours()
    gx.contour_core = core
    try:
        propagate(gx)
        # read what every contour holds before the graph is restored
        contour_contents: dict[
            tuple["python.Class", int], dict[str, infer.Types]
        ] = {}
        frontier = set(core.owned_contours())
        for _ in range(SIGNATURE_ROUNDS):
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
                        # unowned contours reached from owned ones need a
                        # signature too, or a list holding one never looks
                        # like a list holding an equal owned one
                        if item not in contour_contents and is_container(item[0]):
                            following.add(item)
            frontier = following

        templates = (
            contours_report.collect_templates(gx, sites)
            if logger.isEnabledFor(logging.DEBUG)
            else []
        )
    finally:
        gx.open_contours = None
        gx.contour_core = None
        infer.restore_network(gx, pristine)
        for klass, dcpa in core.baseline_dcpa.items():
            klass.dcpa = dcpa

    return SweepResult(contour_contents, templates)


def run_rounds(
    gx: "config.GlobalInfo", sites: list[AllocationSite]
) -> FrozenCore:
    """Run rounds until one changes nothing (see the module header)."""
    containers = [site for site in sites if is_container(site.cl)]
    module_sites = [site for site in containers if site.module_level]
    molds = len(containers) - len(module_sites)
    logger.debug(
        "[contours: %d module-level container site(s);"
        " %d in-function mold(s) to be discovered per template]",
        len(module_sites),
        molds,
    )

    core = FrozenCore()
    # never mint contour 1: it has no variable nodes, and builtin molds
    # are typed as contour 1, so giving it nodes would let them flow
    # into user variables
    core.baseline_dcpa = {cl: max(cl.dcpa, 2) for cl in gx.allclasses}
    for site in module_sites:
        core.bind_module_site(site)

    # every sweep starts from this graph. Molds keep their pristine types
    # throughout, and are what seed_template and note_mold read them for.
    pristine = infer.backup_network(gx)
    gx.orig_types = {
        node: types.copy() for node, types in gx.types.items() if node.constructor
    }

    history: list[contours_report.RoundStats] = []
    round_no = 0
    last_templates: list[contours_report.TemplateRecord] = []
    while round_no < MAX_ROUNDS:
        round_no += 1
        logger.debug("[contours: round %d]", round_no)

        result = sweep(gx, core, pristine, sites)

        changed = core.resignature(result.contour_contents)
        core.rekey()
        batch = core.mint_batch()
        core.fresh_contours = {binding for _key, binding in batch}
        waiting = core.pending_count()

        for entry in batch:
            contours_report.report_added_site(core, entry, round_no)
        if result.templates:
            last_templates = result.templates

        stats = contours_report.RoundStats(
            round=round_no,
            minted=len(batch),
            waiting=waiting,
            templates=len(result.templates),
            contours=len(core.owned_contours()),
            changed=changed,
            signatures=len(core.signature_ids),
        )
        history.append(stats)
        contours_report.report_round(stats)

        # nothing the next sweep depends on has changed
        if not batch and not changed and not core.deferred:
            break
    else:
        logger.warning(
            "contours: stopped after %d rounds without converging;"
            " see the growth table for whether it was still climbing",
            MAX_ROUNDS,
        )

    contours_report.report_growth(history)
    contours_report.report_core(core, round_no)
    contours_report.report_templates(last_templates)
    return core


def analyze(gx: "config.GlobalInfo") -> None:
    """Entry point: find the contours, then materialize them."""
    logger.info("[analyzing types..]")
    all_sites = collect_allocation_sites(gx)
    # module-level allocations in builtin modules (sys.argv) are sites
    # too; molds in builtin modules are not, since builtin methods are
    # analysed through them
    sites = [
        site
        for site in all_sites
        if not site.builtin or site.module_level
    ]
    builtin_count = len(all_sites) - len(sites)
    contours_report.report_allocation_sites(gx, sites, builtin_count)
    core = run_rounds(gx, sites)
    contours_report.report_site_signatures(gx, core)

    materialize(gx, core)


def materialize(gx: "config.GlobalInfo", core: FrozenCore) -> None:
    """Propagate one final time with the core applied, and keep the result.

    This uses the same freeze as the sweeps, with every owned contour open:
    the names in the core are built from frozen sweeps, and an unfrozen pass
    would produce products that no longer match them.
    """
    baseline_dcpa = {cl: cl.dcpa for cl in gx.allclasses}
    apply_core(gx, core, baseline_dcpa)
    gx.open_contours = core.owned_contours()
    gx.contour_core = core
    core.misses = 0
    try:
        propagate(gx)
    finally:
        gx.contour_core = None
        gx.open_contours = None
    logger.debug(
        "[contours: materialised %d contour(s);"
        " %d site(s) left without a contour of their own]",
        len(core.owned_contours()),
        core.misses,
    )
