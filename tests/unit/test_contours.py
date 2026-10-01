# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.contours, which decides the container contours.

The fixture program (fixtures/alloc_sites.py) is a reduced version of the
amaze example: a class whose method builds a tuple that flows back, through an
instance variable, into that same method's argument. It has exactly four
contour-bearing allocation sites, which makes it easy to assert on.
"""

import argparse
import ast
from pathlib import Path
from typing import NamedTuple

import pytest

from shedskin import graph, infer, contours, contours_report, python
from shedskin.config import GlobalInfo


def _analyze(name):
    """Run the whole pipeline on a fixture program."""
    path = Path(__file__).parent / "fixtures" / name
    options = argparse.Namespace()
    gx = GlobalInfo(options)
    gx.silent = True
    gx.source_root = path.parent
    gx.module_path = path
    module_name = path.stem
    gx.main_module = graph.parse_module(module_name, gx)
    infer.analyze(gx, module_name)
    return gx


@pytest.fixture(scope="module")
def analyzed_alloc_sites():
    return _analyze("alloc_sites.py")


@pytest.fixture(scope="module")
def analyzed_global_sites():
    return _analyze("global_sites.py")


def program_sites(gx):
    """The allocation sites written in the program itself."""
    return [s for s in contours.collect_allocation_sites(gx) if not s.builtin]


def kind(site):
    return contours_report.site_kind(site)


class SweptSite(NamedTuple):
    """What sweeping one site on its own found."""

    contour: int
    held: dict
    core: "contours.FrozenCore"
    result: "contours.SweepResult"


def sweep_site(gx, site):
    """Sweep a single module-level container site over a core of its own."""
    core = contours.FrozenCore()
    core.baseline_dcpa = {cl: cl.dcpa for cl in gx.allclasses}
    core.bind_module_site(site)
    pristine = infer.backup_network(gx)
    result = contours.sweep(gx, core, pristine, [site])
    binding = core.bindings[site.node]
    return SweptSite(binding[1], result.contour_contents[binding], core, result)


def fake_class(ident, builtin):
    """A python.Class with just enough set to classify it."""
    cl = python.Class.__new__(python.Class)
    cl.ident = ident
    cl.mv = type("FakeMv", (), {"module": type("M", (), {"builtin": builtin})()})()
    return cl


class TestIsContainer:
    """Only builtin containers are split into contours."""

    def test_builtin_containers(self):
        for ident in ("list", "dict", "set", "tuple", "tuple2", "__iter"):
            assert contours.is_container(fake_class(ident, builtin=True))

    def test_scalars_are_not(self):
        for ident in ("int_", "float_", "str_", "bytes_", "none", "bool_"):
            assert not contours.is_container(fake_class(ident, builtin=True))

    def test_user_class_is_not(self):
        assert not contours.is_container(fake_class("Solver", builtin=False))

    def test_user_class_named_like_container_is_not(self):
        """A user class called 'list' is not a builtin container."""
        assert not contours.is_container(fake_class("list", builtin=False))

    def test_non_classes_are_not(self):
        assert not contours.is_container("list")
        assert not contours.is_container(None)


class TestCollectAllocationSites:
    """Tests for collect_allocation_sites on the fixture program."""

    def test_builtins_are_included(self, analyzed_alloc_sites):
        sites = contours.collect_allocation_sites(analyzed_alloc_sites)
        assert any(site.builtin for site in sites)
        assert any(not site.builtin for site in sites)

    def test_contour_bearing_sites(self, analyzed_alloc_sites):
        """The fixture has one list, two tuple2 and one Solver allocation."""
        contoured = sorted(
            (kind(site), site.cl.ident)
            for site in program_sites(analyzed_alloc_sites)
            if kind(site) != "scalar"
        )
        assert contoured == [
            ("container", "list"),
            ("container", "tuple2"),
            ("container", "tuple2"),
            ("instance", "Solver"),
        ]

    def test_contour_bearing_sites_have_source_locations(
        self, analyzed_alloc_sites
    ):
        """Real allocations come from source, unlike synthesized scalar nodes."""
        for site in program_sites(analyzed_alloc_sites):
            if kind(site) != "scalar":
                assert site.lineno is not None
                assert contours_report.site_location(site).startswith("alloc_sites:")

    def test_both_tuple_sites_start_in_the_same_contour(
        self, analyzed_alloc_sites
    ):
        """The two tuple2 sites are allocated at the same initial dcpa.

        This confluence is what splitting contours exists to resolve, so it is
        worth pinning down: if it ever stops holding, the fixture is no longer
        exercising what it was written for.
        """
        tuple_dcpas = {
            site.dcpa
            for site in program_sites(analyzed_alloc_sites)
            if site.cl.ident == "tuple2"
        }
        assert len(tuple_dcpas) == 1

    def test_ordering_is_deterministic(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        first = contours.collect_allocation_sites(gx)
        second = contours.collect_allocation_sites(gx)
        assert [site.node for site in first] == [site.node for site in second]

    def test_scope_names_enclosing_function(self, analyzed_alloc_sites):
        scopes = {
            contours_report.site_scope(site)
            for site in program_sites(analyzed_alloc_sites)
            if kind(site) != "scalar"
        }
        assert "Solver.__init__" in scopes
        assert "Solver.neighbours" in scopes
        assert "<module>" in scopes


class TestNodeSource:
    """Tests for rendering an allocating expression back to source."""

    def _source(self, text):
        return contours_report.node_source(ast.parse(text, mode="eval").body)

    def test_unparses_expression(self):
        assert self._source("[(x - 1, y)]") == "[(x - 1, y)]"

    def test_collapses_to_one_line(self):
        assert "\n" not in self._source("[\n    1,\n    2,\n]")

    def test_truncates_long_expressions(self):
        text = self._source(str(list(range(100))))
        assert len(text) == contours_report.SOURCE_MAXLEN
        assert text.endswith("...")

    def test_short_expressions_are_not_truncated(self):
        assert self._source("(0, 0)") == "(0, 0)"

    def test_falls_back_for_non_ast_nodes(self):
        """Some constructor nodes hold shedskin objects, not AST nodes."""
        text = contours_report.node_source(object())
        assert text.startswith("<") and text.endswith(">")

    def test_real_sites_render_their_source(self, analyzed_alloc_sites):
        rendered = {
            contours_report.node_source(site.node)
            for site in program_sites(analyzed_alloc_sites)
            if kind(site) != "scalar"
        }
        assert "(0, 0)" in rendered
        assert "[(x - 1, y)]" in rendered
        assert "Solver()" in rendered


class TestContourCensus:
    """After analysis, a container written in a method that is reached from
    several contexts has a copy per template."""

    def _instances(self, gx):
        instances = {}
        for (thing, dcpa, cpa), cnode in gx.cnode.items():
            if cnode.constructor:
                instances.setdefault(thing, set()).add((dcpa, cpa))
        return instances

    def test_base_instance_is_present(self, analyzed_alloc_sites):
        """(0, 0) is the mold itself, so it is always an instance."""
        instances = self._instances(analyzed_alloc_sites)
        for site in program_sites(analyzed_alloc_sites):
            assert (0, 0) in instances[site.node]

    def test_containers_gain_instances(self, analyzed_alloc_sites):
        instances = self._instances(analyzed_alloc_sites)
        counts = [
            len(instances[site.node])
            for site in program_sites(analyzed_alloc_sites)
            if kind(site) == "container"
        ]
        assert max(counts) > 1


class TestFormatTypes:
    """Tests for rendering type sets."""

    class FakeClass:
        def __init__(self, ident):
            self.ident = ident

    def test_empty(self):
        assert contours_report.format_types(set()) == "-"

    def test_sorted_and_labelled_with_contour(self):
        a = self.FakeClass("tuple2")
        b = self.FakeClass("int_")
        text = contours_report.format_types({(a, 1), (b, 0)})
        assert text == "int_(0), tuple2(1)"


class TestModuleLevelVersusMold:
    """Only module-level nodes are allocation sites already."""

    def test_fixture_classification(self, analyzed_alloc_sites):
        sites = [
            s for s in program_sites(analyzed_alloc_sites) if kind(s) != "scalar"
        ]
        source = contours_report.node_source
        module_level = [source(s.node) for s in sites if s.module_level]
        molds = sorted(source(s.node) for s in sites if not s.module_level)
        assert module_level == ["Solver()"]
        assert molds == ["(0, 0)", "(x - 1, y)", "[(x - 1, y)]"]

    def test_global_fixture_is_all_module_level(self, analyzed_global_sites):
        sites = [
            s for s in program_sites(analyzed_global_sites) if kind(s) != "scalar"
        ]
        assert sites
        assert all(s.module_level for s in sites)

    def test_molds_are_refused(self, analyzed_alloc_sites):
        """Binding a mold would share one contour across every template."""
        mold = next(
            s
            for s in program_sites(analyzed_alloc_sites)
            if not s.module_level and kind(s) != "scalar"
        )
        with pytest.raises(AssertionError):
            sweep_site(analyzed_alloc_sites, mold)


class TestSweepOneSite:
    """A container site gets its own contour, and what arrives is read back."""

    def _sites(self, gx):
        return {
            contours_report.node_source(site.node): site
            for site in program_sites(gx)
            if kind(site) == "container" and site.module_level
        }

    def test_instances_are_refused(self, analyzed_global_sites):
        """User classes are never split, so they cannot own a contour."""
        instance = next(
            s
            for s in program_sites(analyzed_global_sites)
            if kind(s) == "instance" and s.module_level
        )
        with pytest.raises(AssertionError):
            sweep_site(analyzed_global_sites, instance)

    def test_sweep_uses_a_fresh_contour(self, analyzed_global_sites):
        gx = analyzed_global_sites
        site = self._sites(gx)["[1, 2, 3]"]
        before = site.cl.dcpa
        assert sweep_site(gx, site).contour == before

    def test_sweep_restores_the_network(self, analyzed_global_sites):
        """Sweeps must be independent, so nothing may survive one."""
        gx = analyzed_global_sites
        site = self._sites(gx)["[1, 2, 3]"]
        before_dcpa = site.cl.dcpa
        before_types = sum(len(t) for t in gx.types.values())
        before_cnodes = len(gx.cnode)

        sweep_site(gx, site)

        assert site.cl.dcpa == before_dcpa
        assert sum(len(t) for t in gx.types.values()) == before_types
        assert len(gx.cnode) == before_cnodes

    def test_open_contours_are_cleared(self, analyzed_global_sites):
        """The freeze must not outlive the sweep that set it."""
        gx = analyzed_global_sites
        assert gx.open_contours is None
        sweep_site(gx, self._sites(gx)["[1, 2, 3]"])
        assert gx.open_contours is None
        assert gx.contour_core is None

    def test_frozen_contours_gain_nothing(self, analyzed_global_sites):
        """Only the contour under test may receive inflow."""
        gx = analyzed_global_sites
        sites = self._sites(gx)
        other = sites["{'a': 1}"]

        def held():
            return {
                name: node.types().copy()
                for name, node in contours.contour_variables(
                    gx, other.cl, other.dcpa
                ).items()
            }

        before = held()
        sweep_site(gx, sites["[1, 2, 3]"])
        assert held() == before

    def test_repeated_sweeps_agree(self, analyzed_global_sites):
        """Same site, same answer: a sweep is observational only."""
        gx = analyzed_global_sites
        site = self._sites(gx)["[1, 2, 3]"]
        assert sweep_site(gx, site).held == sweep_site(gx, site).held

    def test_list_contents(self, analyzed_global_sites):
        gx = analyzed_global_sites
        held = sweep_site(gx, self._sites(gx)["[1, 2, 3]"]).held
        assert {cl.ident for cl, _d in held["unit"]} == {"int_"}

    def test_dict_contents(self, analyzed_global_sites):
        gx = analyzed_global_sites
        held = sweep_site(gx, self._sites(gx)["{'a': 1}"]).held
        assert {cl.ident for cl, _d in held["unit"]} == {"str_"}
        assert {cl.ident for cl, _d in held["value"]} == {"int_"}

    def test_other_contours_are_unchanged(self, analyzed_global_sites):
        """Sweeping must not add anything to any existing contour."""
        gx = analyzed_global_sites

        def snapshot():
            return {
                (node.thing, node.dcpa): frozenset(types)
                for node, types in gx.types.items()
                if isinstance(node.thing, python.Variable)
                and isinstance(node.thing.parent, python.Class)
            }

        before = snapshot()
        for site in self._sites(gx).values():
            sweep_site(gx, site)
        assert snapshot() == before


class TestRunRounds:
    """The whole round loop, on the module-level fixture."""

    def test_binds_the_module_level_containers(self, analyzed_global_sites):
        gx = analyzed_global_sites
        core = contours.run_rounds(gx, contours.collect_allocation_sites(gx))
        bound = {cl.ident for cl, _contour in core.bindings.values()}
        assert bound == {"list", "dict"}
        assert len(set(core.bindings.values())) == len(core.bindings)
        assert set(core.bindings.values()) <= set(core.contour_signature)

    def test_is_deterministic(self, analyzed_global_sites):
        gx = analyzed_global_sites
        sites = contours.collect_allocation_sites(gx)
        first = contours.run_rounds(gx, sites)
        second = contours.run_rounds(gx, sites)
        assert first.bindings == second.bindings
        assert first.contour_signature == second.contour_signature

    def test_leaves_the_network_restored(self, analyzed_global_sites):
        gx = analyzed_global_sites
        before_types = sum(len(t) for t in gx.types.values())
        before_cnodes = len(gx.cnode)

        contours.run_rounds(gx, contours.collect_allocation_sites(gx))

        assert sum(len(t) for t in gx.types.values()) == before_types
        assert len(gx.cnode) == before_cnodes
        assert gx.open_contours is None
        assert gx.contour_core is None


class TestTemplates:
    """Templates created by propagation, and the molds inside them."""

    def _records(self, gx):
        return contours_report.collect_templates(gx, program_sites(gx))

    def test_templates_are_created(self, analyzed_alloc_sites):
        records = self._records(analyzed_alloc_sites)
        assert any(not r.builtin for r in records)
        assert any(r.builtin for r in records)

    def test_polymorphic_call_gets_one_template_per_argument_type(
        self, analyzed_alloc_sites
    ):
        """neighbours() is called with a tuple2 and with None: two templates."""
        records = self._records(analyzed_alloc_sites)
        argsets = {
            r.signature() for r in records if r.name().endswith("Solver.neighbours")
        }
        assert len(argsets) >= 2
        assert any("none(" in sig for sig in argsets)
        assert any("tuple2(" in sig for sig in argsets)

    def test_molds_become_sites_in_each_template(self, analyzed_alloc_sites):
        """Each neighbours template holds its own copy of both molds."""
        for record in self._records(analyzed_alloc_sites):
            if record.name().endswith("Solver.neighbours"):
                sources = sorted(
                    contours_report.node_source(mold.node) for mold, _a in record.molds
                )
                assert sources == ["(x - 1, y)", "[(x - 1, y)]"]

    def test_molds_get_a_contour_in_every_template(self, analyzed_alloc_sites):
        """A mold allocates a single class in each template it appears in."""
        found = False
        for record in self._records(analyzed_alloc_sites):
            for mold, alloc in record.molds:
                assert alloc is not None, mold
                cl, dcpa = alloc
                assert cl is mold.cl
                assert dcpa >= 0
                found = True
        assert found

    def test_module_level_sites_are_not_molds(self, analyzed_alloc_sites):
        grouped = contours_report.molds_by_function(program_sites(analyzed_alloc_sites))
        for molds in grouped.values():
            assert all(not m.module_level for m in molds)
            assert all(kind(m) != "scalar" for m in molds)

    def test_signature_renders_receiver_and_arguments(self, analyzed_alloc_sites):
        records = self._records(analyzed_alloc_sites)
        init = [r for r in records if r.name().endswith("Solver.__init__")]
        assert init
        assert init[0].signature().startswith("(self=Solver(")


class TestFrozenCoreBookkeeping:
    """The invariants the ownership indexes rest on (no gx needed)."""

    def _core_with_owner(self):
        core = contours.FrozenCore()
        cl = type("FakeClass", (), {"ident": "fake", "dcpa": 2})()
        product = ("f", ((cl, 1),), "node")
        core.discovered[product] = cl
        core.next_contour[cl] = 5
        return core, cl, product

    def test_known_product_is_served_from_the_core(self):
        core = contours.FrozenCore()
        cl = type("FakeClass", (), {"ident": "list", "dcpa": 2})()
        product = ("f", (), ast.parse("[]", mode="eval").body)
        core.owners[product] = (cl, 5)
        assert core.note_mold(None, product, None) == (cl, 5)

    def test_minted_contour_is_owned_and_named(self):
        core, cl, product = self._core_with_owner()
        name, binding = core.mint(product)
        assert binding in core.owned_contours()
        assert core.owners[product] == binding
        assert core.alloc_bindings[name] == binding

    def test_pending_is_pure(self):
        core, cl, product = self._core_with_owner()
        core.fresh_contours = {(cl, 1)}  # product mentions a fresh contour
        before = core.deferred
        assert core.pending(product) is not None  # deferral is mint_batch's call
        assert core.deferred == before

    def test_pending_none_after_mint(self):
        core, cl, product = self._core_with_owner()
        core.mint(product)
        assert core.pending(product) is None
        assert core.pending_count() == 0

    def test_mint_batch_defers_fresh_mentions(self):
        core, cl, product = self._core_with_owner()
        core.fresh_contours = {(cl, 1)}
        assert core.mint_batch() == []
        assert core.deferred == 1
        assert core.pending_count() == 1  # waiting includes deferred
        core.fresh_contours = set()
        assert len(core.mint_batch()) == 1

    def test_rekey_files_the_older_owner_under_a_shared_name(self):
        core, cl, product = self._core_with_owner()
        other = ("f", ((cl, 2),), "node")
        core.owners[product] = (cl, 5)
        core.owners[other] = (cl, 6)
        # both argument contours hold the same thing, so the names coincide
        core.contour_signature = {(cl, 1): 0, (cl, 2): 0}
        core.rekey()
        assert list(core.alloc_bindings.values()) == [(cl, 5)]
        # the younger owner keeps its own contour, found by product
        assert core.note_mold(None, other, None) == (cl, 6)


class TestQuietByDefault:
    def test_reports_are_debug_level(self):
        # the analysis must stay quiet without -d3
        import inspect

        source = inspect.getsource(contours)
        # the one INFO line is the progress message shown to every user
        assert source.count("logger.info(") == 1
        assert 'logger.info("[analyzing types..]")' in source


def _analyze_counting_rounds(name):
    """Analyze a fixture, keeping the core and the number of rounds."""
    cores = []
    rounds = []
    run_rounds, sweep = contours.run_rounds, contours.sweep

    def capture(*args, **kwargs):
        core = run_rounds(*args, **kwargs)
        cores.append(core)
        return core

    def counting_sweep(*args, **kwargs):
        rounds.append(1)
        return sweep(*args, **kwargs)

    contours.run_rounds, contours.sweep = capture, counting_sweep
    try:
        gx = _analyze(name)
    finally:
        contours.run_rounds, contours.sweep = run_rounds, sweep
    gx.test_core = cores[-1]
    gx.test_rounds = len(rounds)
    return gx


def _types_at(gx, thing):
    """Union of the types of every template copy of an AST node."""
    found = set()
    for (node, _dcpa, _cpa), cnode in gx.cnode.items():
        if node is thing:
            found |= cnode.types()
    return found


@pytest.fixture(scope="module")
def lambda_sites():
    return _analyze_counting_rounds("lambda_sites.py")


class TestRegressions:
    """Regressions found while the round loop was being developed."""

    def test_lambda_only_receives_its_argument(self, lambda_sites):
        # the iterator over `self.entries` and the one over `self.offsets`
        # were merged while both were still empty, so map() fed the lambda
        # its own tuples and `entry` became {Entry, tuple2}
        gx = lambda_sites
        lam = gx.main_module.mv.lambdas["__lambda0__"]
        entry = lam.vars["entry"]
        idents = {cl.ident for cl, _ in gx.merged_inh[entry]}
        assert idents == {"Entry"}

    def test_rounds_converge_quickly(self, lambda_sites):
        # the stale-name cycle re-minted four sites every three rounds and
        # never converged; the fixpoint is reached in a handful of rounds
        assert lambda_sites.test_rounds <= 12

    def test_iter_result_has_one_contour(self):
        # class_copy handed every copied method's allocation site the types
        # of the base copy, so `iter([1, 2, 3])` also returned the shared
        # bucket iterator and __product2 got half-filled tuple2 contours
        gx = _analyze_counting_rounds("product_sites.py")
        calls = [
            node
            for node in ast.walk(gx.main_module.ast)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "iter"
        ]
        assert len(calls) == 2
        for call in calls:
            types = _types_at(gx, call)
            assert len(types) == 1, sorted((cl.ident, d) for cl, d in types)

    def test_recursion_through_a_fresh_container_settles(self):
        # a function that creates a list and passes it to itself gave every
        # template a newly minted, still empty list, whose mold was named
        # afresh each round: one more contour per round, forever
        gx = _analyze_counting_rounds("recursive_sites.py")
        assert gx.test_rounds <= 12

    def test_products_named_alike_come_apart(self):
        # two list comprehensions whose inputs were both empty for a round
        # shared one iterator contour by name; when their names came apart
        # the sharing had to end, or `z` stays {int, list}
        gx = _analyze_counting_rounds("shared_iter_sites.py")
        comps = [lc for _node, lc, _parent in gx.main_module.mv.listcomps]
        (z,) = [lc.vars["z"] for lc in comps if "z" in lc.vars]
        idents = {cl.ident for cl, _ in gx.merged_inh[z]}
        assert idents == {"list"}

    def test_bucket_products_are_not_sites(self):
        # a template keyed on the shared bucket contour of a not-yet-bound
        # site is an artefact of the analysis being half-done; minting its
        # molds made which sites exist depend on propagation order, and on
        # mastermind2 one run in a few ended with {float, int, tuple2}
        gx = _analyze_counting_rounds("bucket_sites.py")
        core = gx.test_core
        for product in core.owners:
            assert not core.mentions_bucket(product), contours.repr_cart(product[1])
        best = gx.main_module.mv.funcs["best"]
        idents = {cl.ident for cl, _ in gx.merged_inh[best.vars["play"]]}
        assert idents == {"tuple2"}

    def test_static_method_receiver_is_not_a_bucket(self):
        # a static or class method is analysed at its class's dcpa 1, so its
        # product starts with (cls, 1): that is the class, not a container
        # in a bucket, and the mold inside is a site like any other
        gx = _analyze_counting_rounds("staticmethod_sites.py")
        assert gx.test_core.misses == 0
        d3 = gx.main_module.mv.globals["d3"]
        (binding,) = gx.merged_inh[d3]
        assert binding[0].ident == "defaultdict"
        assert binding in gx.test_core.owners.values()
