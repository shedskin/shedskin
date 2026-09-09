# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.infer2, the experimental v2 type analysis.

The fixture program (fixtures/alloc_sites.py) is a reduced version of the
amaze example: a class whose method builds a tuple that flows back, through an
instance variable, into that same method's argument. It has exactly four
contour-bearing allocation sites, which makes it easy to assert on.
"""

import argparse
import ast
import sys
from pathlib import Path

import pytest

from shedskin import graph, infer, infer2, python
from shedskin.config import GlobalInfo


@pytest.fixture(scope="module")
def analyzed_alloc_sites():
    """Run the full pipeline on the allocation-site fixture program."""
    path = Path(__file__).parent / "fixtures" / "alloc_sites.py"

    options = argparse.Namespace()
    gx = GlobalInfo(options)
    gx.silent = True
    gx.source_root = path.parent
    gx.module_path = path
    gx.infer_v2 = True
    gx.infer_v2_codegen = True

    module_name = path.stem
    gx.main_module = graph.parse_module(module_name, gx)
    infer.analyze(gx, module_name)

    return gx


@pytest.fixture(scope="module")
def analyzed_global_sites():
    """Run the full pipeline on a program whose allocations are module-level."""
    path = Path(__file__).parent / "fixtures" / "global_sites.py"

    options = argparse.Namespace()
    gx = GlobalInfo(options)
    gx.silent = True
    gx.source_root = path.parent
    gx.module_path = path
    gx.infer_v2 = True
    gx.infer_v2_codegen = True

    module_name = path.stem
    gx.main_module = graph.parse_module(module_name, gx)
    infer.analyze(gx, module_name)

    return gx


class TestAllocationSiteKind:
    """Tests for allocation_site_kind classification."""

    class FakeModule:
        def __init__(self, builtin):
            self.builtin = builtin

    class FakeMv:
        def __init__(self, builtin):
            self.module = TestAllocationSiteKind.FakeModule(builtin)

    class FakeClass:
        def __init__(self, ident, builtin=True):
            self.ident = ident
            self.mv = TestAllocationSiteKind.FakeMv(builtin)

    def test_builtin_container_is_container(self):
        for ident in ("list", "dict", "set", "tuple", "tuple2", "__iter"):
            cl = self.FakeClass(ident, builtin=True)
            assert infer2.allocation_site_kind(cl) == infer2.ALLOC_CONTAINER

    def test_scalar_classes_are_scalar(self):
        for ident in ("int_", "float_", "str_", "bytes_", "none", "bool_"):
            cl = self.FakeClass(ident, builtin=True)
            assert infer2.allocation_site_kind(cl) == infer2.ALLOC_SCALAR

    def test_user_class_is_instance(self):
        cl = self.FakeClass("Solver", builtin=False)
        assert infer2.allocation_site_kind(cl) == infer2.ALLOC_INSTANCE

    def test_user_class_named_like_container_is_instance(self):
        """A user class called 'list' is not a builtin container."""
        cl = self.FakeClass("list", builtin=False)
        assert infer2.allocation_site_kind(cl) == infer2.ALLOC_INSTANCE


class TestCollectAllocationSites:
    """Tests for collect_allocation_sites on the fixture program."""

    def test_program_sites_exclude_builtins(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        assert sites
        assert all(not site.builtin for site in sites)

    def test_builtins_are_scanned_when_requested(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        program = infer2.collect_allocation_sites(gx, builtins=False)
        everything = infer2.collect_allocation_sites(gx, builtins=True)
        assert len(everything) > len(program)
        assert any(site.builtin for site in everything)

    def test_contour_bearing_sites(self, analyzed_alloc_sites):
        """The fixture has one list, two tuple2 and one Solver allocation."""
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        contoured = sorted(
            (site.kind, site.cl.ident)
            for site in sites
            if site.kind != infer2.ALLOC_SCALAR
        )
        assert contoured == [
            (infer2.ALLOC_CONTAINER, "list"),
            (infer2.ALLOC_CONTAINER, "tuple2"),
            (infer2.ALLOC_CONTAINER, "tuple2"),
            (infer2.ALLOC_INSTANCE, "Solver"),
        ]

    def test_contour_bearing_sites_have_source_locations(
        self, analyzed_alloc_sites
    ):
        """Real allocations come from source, unlike synthesized scalar nodes."""
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        for site in sites:
            if site.kind != infer2.ALLOC_SCALAR:
                assert site.lineno is not None
                assert site.location().startswith("alloc_sites:")

    def test_both_tuple_sites_start_in_the_same_contour(
        self, analyzed_alloc_sites
    ):
        """The two tuple2 sites are allocated at the same initial dcpa.

        This confluence is the thing contour splitting exists to resolve, so
        it is worth pinning down: if it ever stops holding, the fixture is no
        longer exercising what it was written for.
        """
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        tuple_dcpas = {
            site.dcpa for site in sites if site.cl.ident == "tuple2"
        }
        assert len(tuple_dcpas) == 1

    def test_ordering_is_deterministic(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        first = infer2.collect_allocation_sites(gx, builtins=True)
        second = infer2.collect_allocation_sites(gx, builtins=True)
        assert [site.node for site in first] == [site.node for site in second]

    def test_scope_names_enclosing_function(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        scopes = {
            site.scope() for site in sites if site.kind != infer2.ALLOC_SCALAR
        }
        assert "Solver.__init__" in scopes
        assert "Solver.neighbours" in scopes
        assert "<module>" in scopes


class TestAllocationSiteSource:
    """Tests for rendering an allocation site back to source."""

    class FakeModule:
        builtin = False
        ident = "fake"

    class FakeMv:
        def __init__(self):
            self.module = TestAllocationSiteSource.FakeModule()

    class FakeCNode:
        def __init__(self, thing):
            self.thing = thing
            self.parent = None
            self.mv = TestAllocationSiteSource.FakeMv()

    class FakeClass:
        ident = "list"

    def _site(self, thing):
        return infer2.AllocationSite(
            self.FakeCNode(thing), self.FakeClass(), 1, infer2.ALLOC_CONTAINER
        )

    def test_unparses_expression(self):
        node = ast.parse("[(x - 1, y)]", mode="eval").body
        assert self._site(node).source() == "[(x - 1, y)]"

    def test_collapses_to_one_line(self):
        node = ast.parse("[\n    1,\n    2,\n]", mode="eval").body
        assert "\n" not in self._site(node).source()

    def test_truncates_long_expressions(self):
        node = ast.parse(str(list(range(100))), mode="eval").body
        text = self._site(node).source()
        assert len(text) == infer2.ALLOC_SOURCE_MAXLEN
        assert text.endswith("...")

    def test_respects_explicit_maxlen(self):
        node = ast.parse(str(list(range(100))), mode="eval").body
        assert len(self._site(node).source(maxlen=12)) == 12

    def test_short_expressions_are_not_truncated(self):
        node = ast.parse("(0, 0)", mode="eval").body
        assert self._site(node).source() == "(0, 0)"

    def test_falls_back_for_non_ast_nodes(self):
        """Some constructor nodes hold shedskin objects, not AST nodes."""
        text = self._site(object()).source()
        assert text.startswith("<") and text.endswith(">")

    def test_real_sites_render_their_source(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        rendered = {
            site.source()
            for site in sites
            if site.kind != infer2.ALLOC_SCALAR
        }
        assert "(0, 0)" in rendered
        assert "[(x - 1, y)]" in rendered
        assert "Solver()" in rendered


class TestAllocationSiteInstances:
    """Tests for the post-analysis contour census."""

    def test_every_site_has_at_least_one_instance(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        instances = infer2.allocation_site_instances(gx)
        for site in sites:
            assert len(instances.get(site.node, set())) >= 1

    def test_base_instance_is_present(self, analyzed_alloc_sites):
        """(0, 0) is the base site itself, so it is always an instance."""
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        instances = infer2.allocation_site_instances(gx)
        for site in sites:
            assert (0, 0) in instances[site.node]

    def test_containers_gain_instances(self, analyzed_alloc_sites):
        """Containers in a method reached from several contexts get copies."""
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        instances = infer2.allocation_site_instances(gx)
        counts = [
            len(instances[site.node])
            for site in sites
            if site.kind == infer2.ALLOC_CONTAINER
        ]
        assert max(counts) > 1


class TestFormatTypes:
    """Tests for rendering type sets."""

    class FakeClass:
        def __init__(self, ident):
            self.ident = ident

    def test_empty(self):
        assert infer2.format_types(set()) == "-"

    def test_sorted_and_labelled_with_contour(self):
        a = self.FakeClass("tuple2")
        b = self.FakeClass("int_")
        text = infer2.format_types({(a, 1), (b, 0)})
        assert text == "int_(0), tuple2(1)"


class TestModuleLevelVersusMold:
    """Only module-level nodes are allocation sites already."""

    def test_fixture_classification(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        sites = [
            s
            for s in infer2.collect_allocation_sites(gx, builtins=False)
            if s.kind != infer2.ALLOC_SCALAR
        ]
        module_level = [s.source() for s in sites if s.module_level]
        molds = sorted(s.source() for s in sites if not s.module_level)
        assert module_level == ["Solver()"]
        assert molds == ["(0, 0)", "(x - 1, y)", "[(x - 1, y)]"]

    def test_global_fixture_is_all_module_level(self, analyzed_global_sites):
        gx = analyzed_global_sites
        sites = [
            s
            for s in infer2.collect_allocation_sites(gx, builtins=False)
            if s.kind != infer2.ALLOC_SCALAR
        ]
        assert sites
        assert all(s.module_level for s in sites)

    def test_molds_are_refused(self, analyzed_alloc_sites):
        """Probing a mold would share one contour across every template."""
        gx = analyzed_alloc_sites
        mold = next(
            s
            for s in infer2.collect_allocation_sites(gx, builtins=False)
            if not s.module_level and s.kind != infer2.ALLOC_SCALAR
        )
        with pytest.raises(AssertionError):
            infer2.probe_allocation_site(gx, mold)


class TestProbeAllocationSite:
    """Stage 2: give a container site its own contour and see what arrives."""

    def _sites(self, gx):
        return {
            site.source(): site
            for site in infer2.collect_allocation_sites(gx, builtins=False)
            if site.kind == infer2.ALLOC_CONTAINER and site.module_level
        }

    def test_instances_are_refused(self, analyzed_global_sites):
        """User classes are never split, so probing one says nothing."""
        gx = analyzed_global_sites
        instance = next(
            s
            for s in infer2.collect_allocation_sites(gx, builtins=False)
            if s.kind == infer2.ALLOC_INSTANCE and s.module_level
        )
        with pytest.raises(AssertionError):
            infer2.probe_allocation_site(gx, instance)

    def test_probe_uses_a_fresh_contour(self, analyzed_global_sites):
        gx = analyzed_global_sites
        site = self._sites(gx)["[1, 2, 3]"]
        before = site.cl.dcpa
        assert infer2.probe_allocation_site(gx, site).contour == before

    def test_probe_restores_the_network(self, analyzed_global_sites):
        """Probes must be independent, so nothing may survive one."""
        gx = analyzed_global_sites
        site = self._sites(gx)["[1, 2, 3]"]
        before_dcpa = site.cl.dcpa
        before_types = sum(len(t) for t in gx.types.values())
        before_cnodes = len(gx.cnode)

        infer2.probe_allocation_site(gx, site)

        assert site.cl.dcpa == before_dcpa
        assert sum(len(t) for t in gx.types.values()) == before_types
        assert len(gx.cnode) == before_cnodes

    def test_open_contour_is_cleared(self, analyzed_global_sites):
        """The freeze must not outlive the probe that set it."""
        gx = analyzed_global_sites
        assert gx.infer_v2_open_contours is None
        infer2.probe_allocation_site(gx, self._sites(gx)["[1, 2, 3]"])
        assert gx.infer_v2_open_contours is None

    def test_frozen_contours_gain_nothing(self, analyzed_global_sites):
        """Only the contour under test may receive inflow."""
        gx = analyzed_global_sites
        sites = self._sites(gx)
        other = sites["{'a': 1}"]
        before = {
            name: node.types().copy()
            for name, node in infer2.contour_variables(
                gx, other.cl, other.dcpa
            ).items()
        }
        infer2.probe_allocation_site(gx, sites["[1, 2, 3]"])
        after = {
            name: node.types()
            for name, node in infer2.contour_variables(
                gx, other.cl, other.dcpa
            ).items()
        }
        assert after == before

    def test_repeated_probes_agree(self, analyzed_global_sites):
        """Same site, same answer: the probe is observational only."""
        gx = analyzed_global_sites
        site = self._sites(gx)["[1, 2, 3]"]
        first = infer2.probe_allocation_site(gx, site).inflow
        second = infer2.probe_allocation_site(gx, site).inflow
        assert first == second

    def test_list_inflow(self, analyzed_global_sites):
        gx = analyzed_global_sites
        inflow = infer2.probe_allocation_site(
            gx, self._sites(gx)["[1, 2, 3]"]
        ).inflow
        assert {cl.ident for cl, _d in inflow["unit"]} == {"int_"}

    def test_dict_inflow(self, analyzed_global_sites):
        gx = analyzed_global_sites
        inflow = infer2.probe_allocation_site(
            gx, self._sites(gx)["{'a': 1}"]
        ).inflow
        assert {cl.ident for cl, _d in inflow["unit"]} == {"str_"}
        assert {cl.ident for cl, _d in inflow["value"]} == {"int_"}

    def test_probe_converges_quickly(self, analyzed_global_sites):
        """A probe that needs the whole safety bound is not converging."""
        gx = analyzed_global_sites
        for site in self._sites(gx).values():
            result = infer2.probe_allocation_site(gx, site)
            assert result.rounds < infer2.V2_PROBE_ROUNDS


class TestProbeReachability:
    """Module-level container sites always allocate their contour."""

    def test_module_level_containers_are_reached(self, analyzed_global_sites):
        gx = analyzed_global_sites
        probed = 0
        for site in infer2.collect_allocation_sites(gx, builtins=False):
            if site.kind != infer2.ALLOC_CONTAINER or not site.module_level:
                continue
            assert infer2.probe_allocation_site(gx, site).reached
            probed += 1
        assert probed >= 2


class TestFrozenCore:
    """While one contour is open, every other contour is read-only."""

    def _container_sites(self, gx):
        return {
            site.source(): site
            for site in infer2.collect_allocation_sites(gx, builtins=False)
            if site.kind == infer2.ALLOC_CONTAINER and site.module_level
        }

    def test_open_contour_is_cleared_afterwards(self, analyzed_global_sites):
        gx = analyzed_global_sites
        site = self._container_sites(gx)["[1, 2, 3]"]
        infer2.probe_allocation_site(gx, site)
        assert gx.infer_v2_open_contours is None

    def test_other_contours_are_unchanged(self, analyzed_global_sites):
        """Probing one site must not add anything to any other contour."""
        gx = analyzed_global_sites

        def snapshot():
            return {
                (node.thing, node.dcpa): frozenset(types)
                for node, types in gx.types.items()
                if isinstance(node.thing, python.Variable)
                and isinstance(node.thing.parent, python.Class)
            }

        before = snapshot()
        for site in self._container_sites(gx).values():
            infer2.probe_allocation_site(gx, site)
        assert snapshot() == before

    def test_probe_still_sees_direct_inflow(self, analyzed_global_sites):
        """Freezing must not block what flows straight into the open contour."""
        gx = analyzed_global_sites
        inflow = infer2.probe_allocation_site(
            gx, self._container_sites(gx)["[1, 2, 3]"]
        ).inflow
        assert {cl.ident for cl, _d in inflow["unit"]} == {"int_"}


class TestFrozenCoreAccumulation:
    """The core only grows, and sites keep the contour they were given."""

    def test_learn_returns_only_new_types(self):
        core = infer2.FrozenCore()

        class FakeClass:
            ident = "list"

        cl = FakeClass()
        first = core.learn(cl, 7, "unit", {("int_", 0)})
        assert first == {("int_", 0)}
        again = core.learn(cl, 7, "unit", {("int_", 0)})
        assert again == set()
        more = core.learn(cl, 7, "unit", {("str_", 0)})
        assert more == {("str_", 0)}
        assert core.contents[(cl, 7, "unit")] == {("int_", 0), ("str_", 0)}

    def test_contours_are_allocated_once(self, analyzed_global_sites):
        gx = analyzed_global_sites
        core = infer2.FrozenCore()
        baseline = {cl: cl.dcpa for cl in gx.allclasses}
        sites = [
            s
            for s in infer2.collect_allocation_sites(gx, builtins=False)
            if s.kind == infer2.ALLOC_CONTAINER and s.module_level
        ]
        first = [core.contour_for(s, baseline) for s in sites]
        second = [core.contour_for(s, baseline) for s in sites]
        assert first == second

    def test_sites_of_a_class_get_distinct_contours(self, analyzed_global_sites):
        gx = analyzed_global_sites
        core = infer2.FrozenCore()
        baseline = {cl: cl.dcpa for cl in gx.allclasses}
        for site in infer2.collect_allocation_sites(gx, builtins=False):
            if site.kind == infer2.ALLOC_CONTAINER and site.module_level:
                core.contour_for(site, baseline)
        assert len(set(core.bindings.values())) == len(core.bindings)

    def test_sweep_converges_and_reports_a_core(self, analyzed_global_sites):
        gx = analyzed_global_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        core = infer2.probe_allocation_sites(gx, sites)
        assert core.bindings
        assert core.contents
        # the fixture's own module-level sites are a list and a dict; the
        # builtin module contributes container molds of its own (a tuple
        # site in a builtin __init__ among them), so only check inclusion
        bound = {cl.ident for cl, _contour in core.bindings.values()}
        assert bound == {"list", "dict"}
        observed = {key[0].ident for key in core.contents}
        assert {"list", "dict"} <= observed

    def test_reprobing_does_not_depend_on_leftover_alloc_info(
        self, analyzed_global_sites
    ):
        # the answer ifa_seed_template gets for a mold comes from the core,
        # not from a memo in gx.alloc_info: probing with whatever a previous
        # run left there and probing with it cleared give the same core
        gx = analyzed_global_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        with_leftovers = infer2.probe_allocation_sites(gx, sites)
        gx.alloc_info = {}
        cleared = infer2.probe_allocation_sites(gx, sites)
        assert set(with_leftovers.contents) == set(cleared.contents)
        assert with_leftovers.bindings == cleared.bindings

    def test_sweeping_leaves_the_network_restored(self, analyzed_global_sites):
        gx = analyzed_global_sites
        before_types = sum(len(t) for t in gx.types.values())
        before_cnodes = len(gx.cnode)
        before_dcpa = {cl: cl.dcpa for cl in gx.allclasses}

        infer2.probe_allocation_sites(
            gx, infer2.collect_allocation_sites(gx, builtins=False)
        )

        assert sum(len(t) for t in gx.types.values()) == before_types
        assert len(gx.cnode) == before_cnodes
        assert {cl: cl.dcpa for cl in gx.allclasses} == before_dcpa
        assert gx.infer_v2_open_contours is None


class TestTemplates:
    """Stage 3: templates created by propagation, and the molds inside them."""

    def _records(self, gx):
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        core = infer2.FrozenCore()
        baseline = {cl: cl.dcpa for cl in gx.allclasses}
        result = infer2.sweep_once(
            gx, [], core, baseline, probes_and_molds=sites,
            collect=True, freeze=False,
        )
        templates = result.templates
        return templates

    def test_templates_are_created(self, analyzed_alloc_sites):
        records = self._records(analyzed_alloc_sites)
        assert records
        assert any(not r.builtin for r in records)
        assert any(r.builtin for r in records)

    def test_polymorphic_call_gets_one_template_per_argument_type(
        self, analyzed_alloc_sites
    ):
        """neighbours() is called with a tuple2 and with None: two templates."""
        records = self._records(analyzed_alloc_sites)
        neighbours = [
            r for r in records if r.name().endswith("Solver.neighbours")
        ]
        argsets = {r.signature() for r in neighbours}
        assert len(argsets) >= 2
        assert any("none(" in sig for sig in argsets)
        assert any("tuple2(" in sig for sig in argsets)

    def test_molds_become_sites_in_each_template(self, analyzed_alloc_sites):
        """Each neighbours template holds its own copy of both molds."""
        records = self._records(analyzed_alloc_sites)
        for record in records:
            if not record.name().endswith("Solver.neighbours"):
                continue
            sources = sorted(mold.source() for mold, _a in record.molds)
            assert sources == ["(x - 1, y)", "[(x - 1, y)]"]

    def test_molds_get_a_contour_in_every_template(self, analyzed_alloc_sites):
        """A mold allocates a single class in each template it appears in."""
        records = self._records(analyzed_alloc_sites)
        found = False
        for record in records:
            for mold, alloc in record.molds:
                assert alloc is not None, mold
                cl, dcpa = alloc
                assert cl is mold.cl
                assert dcpa >= 0
                found = True
        assert found

    def test_module_level_sites_are_not_molds(self, analyzed_alloc_sites):
        gx = analyzed_alloc_sites
        sites = infer2.collect_allocation_sites(gx, builtins=False)
        grouped = infer2.molds_by_function(sites)
        for molds in grouped.values():
            assert all(not m.module_level for m in molds)
            assert all(m.kind != infer2.ALLOC_SCALAR for m in molds)

    def test_signature_renders_receiver_and_arguments(self, analyzed_alloc_sites):
        records = self._records(analyzed_alloc_sites)
        init = [r for r in records if r.name().endswith("Solver.__init__")]
        assert init
        assert init[0].signature().startswith("(self=Solver(")


class TestNoteMoldLeavesAllocInfoAlone:
    """note_mold answers from the core; gx.alloc_info is not a v2 memo."""

    def test_known_site_is_served_without_writing_alloc_info(self):
        core = infer2.FrozenCore()
        cl = type("FakeClass", (), {"ident": "list", "dcpa": 2})()
        product = ("f", (), ast.parse("[]", mode="eval").body)
        core.owners[product] = (cl, 5)
        gx = type("FakeGx", (), {"alloc_info": {}})()
        assert core.note_mold(gx, product, None) == (cl, 5)
        assert gx.alloc_info == {}


class TestFrozenCoreBookkeeping:
    """The invariants the ownership indexes rest on (no gx needed)."""

    def _core_with_owner(self):
        core = infer2.FrozenCore()
        cl = type("FakeClass", (), {"ident": "fake", "dcpa": 2})()
        product = ("f", ((cl, 1),), "node")
        core.discovered[product] = cl
        core.next_contour[cl] = 5
        return core, cl, product

    def test_minted_contour_is_owned(self):
        core, cl, product = self._core_with_owner()
        _key, binding = core.mint(product)
        assert binding in core.owned_contours()
        assert core.owners[product] == binding
        assert binding in core.provisional.values()

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
        assert core.mint_batch(sys.maxsize) == []
        assert core.deferred == 1
        assert core.pending_count() == 1  # waiting includes deferred
        core.fresh_contours = set()
        assert len(core.mint_batch(sys.maxsize)) == 1


class TestSitesPerRound:
    def test_default_is_unlimited(self, monkeypatch):
        monkeypatch.delenv("SS_V2_SITES_PER_ROUND", raising=False)
        assert infer2.sites_per_round() == sys.maxsize

    def test_empty_is_unlimited(self):
        assert infer2.sites_per_round("") == sys.maxsize
        assert infer2.sites_per_round("  ") == sys.maxsize

    def test_explicit_limit(self, monkeypatch):
        monkeypatch.setenv("SS_V2_SITES_PER_ROUND", "3")
        assert infer2.sites_per_round() == 3
        assert infer2.sites_per_round("1") == 1

    def test_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            infer2.sites_per_round("0")
        with pytest.raises(ValueError):
            infer2.sites_per_round("-2")

    def test_reports_are_debug_level(self):
        # v2 reporting must stay quiet without -d3
        import inspect
        source = inspect.getsource(infer2)
        # the one INFO line is the progress message shown to every user
        assert source.count("logger.info(") == 1
        assert 'logger.info("[analyzing types..]")' in source


def _analyze_v2(name):
    """Run the whole v2 pipeline, materialisation included, on a fixture."""
    path = Path(__file__).parent / "fixtures" / name
    options = argparse.Namespace()
    gx = GlobalInfo(options)
    gx.silent = True
    gx.source_root = path.parent
    gx.module_path = path
    gx.infer_v2 = True
    gx.infer_v2_codegen = True
    module_name = path.stem
    gx.main_module = graph.parse_module(module_name, gx)
    cores = []
    probe = infer2.probe_allocation_sites

    def capture(*args, **kwargs):
        core = probe(*args, **kwargs)
        cores.append(core)
        return core

    infer2.probe_allocation_sites = capture
    try:
        infer.analyze(gx, module_name)
    finally:
        infer2.probe_allocation_sites = probe
    gx.v2_core = cores[-1]
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
    return _analyze_v2("lambda_sites.py")


class TestBatchMinting:
    """Regressions found on c64 once every discovered site is minted per
    round (SS_V2_SITES_PER_ROUND unlimited): naming must survive signatures
    moving, and a copied method must not leak the bucket contour."""

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
        assert lambda_sites.v2_core.rounds <= 12

    def test_iter_result_has_one_contour(self):
        # class_copy handed every copied method's allocation site the types
        # of the base copy, so `iter([1, 2, 3])` also returned the shared
        # bucket iterator and __product2 got half-filled tuple2 contours
        gx = _analyze_v2("product_sites.py")
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
        # a method that creates a list and passes it to itself gave every
        # template a newly minted, still empty list, whose mold was named
        # afresh each round: one more contour per round, forever
        gx = _analyze_v2("recursive_sites.py")
        assert gx.v2_core.rounds <= 12

    def test_products_named_alike_come_apart(self):
        # two list comprehensions whose inputs were both empty for a round
        # shared one iterator contour by name; when their names came apart
        # the sharing had to end, or `z` stays {int, list}
        gx = _analyze_v2("shared_iter_sites.py")
        comps = [lc for _node, lc, _parent in gx.main_module.mv.listcomps]
        (z,) = [lc.vars["z"] for lc in comps if "z" in lc.vars]
        idents = {cl.ident for cl, _ in gx.merged_inh[z]}
        assert idents == {"list"}

    def test_bucket_products_are_not_sites(self):
        # a template keyed on the shared bucket contour of a not-yet-bound
        # site is an artefact of the analysis being half-done; minting its
        # molds made which sites exist depend on propagation order, and on
        # mastermind2 one run in a few ended with {float, int, tuple2}
        gx = _analyze_v2("bucket_sites.py")
        core = gx.v2_core
        for product in core.owners:
            assert not core.mentions_bucket(product), infer2.repr_cart(product[1])
        best = gx.main_module.mv.funcs["best"]
        idents = {cl.ident for cl, _ in gx.merged_inh[best.vars["play"]]}
        assert idents == {"tuple2"}

    def test_static_method_receiver_is_not_a_bucket(self):
        # a static or class method is analysed at its class's dcpa 1, so its
        # product starts with (cls, 1): that is the class, not a container
        # in a bucket, and the mold inside is a site like any other
        gx = _analyze_v2("staticmethod_sites.py")
        assert gx.v2_core.misses == 0
        mv = gx.main_module.mv
        d3 = mv.globals["d3"]
        (binding,) = gx.merged_inh[d3]
        assert binding[0].ident == "defaultdict"
        assert binding in gx.v2_core.owners.values()
