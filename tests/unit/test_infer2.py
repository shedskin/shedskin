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
    # not gx.infer_v2: analyze() would run v2 and stop instead of returning

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
    # not gx.infer_v2: analyze() would run v2 and stop instead of returning

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
        idents = {
            cl.ident
            for key in core.contents
            for cl in [key[0]]
        }
        assert idents <= {"list", "dict"}

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
        _r, _n, _u, templates = infer2.sweep_once(
            gx, [], core, baseline, probes_and_molds=sites,
            collect=True, freeze=False,
        )
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
