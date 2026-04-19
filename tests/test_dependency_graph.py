import pytest
from assetpacker.dependency_graph import DependencyGraph


@pytest.fixture
def graph():
    g = DependencyGraph()
    g.add("a.png", ["b.png", "c.png"])
    g.add("b.png", ["c.png"])
    return g


def test_dependencies_returns_direct(graph):
    assert graph.dependencies("a.png") == ["b.png", "c.png"]


def test_dependencies_empty_for_leaf(graph):
    assert graph.dependencies("c.png") == []


def test_dependents_of_shared_dep(graph):
    assert graph.dependents("c.png") == ["a.png", "b.png"]


def test_all_assets_includes_leaves(graph):
    assets = graph.all_assets()
    assert "a.png" in assets
    assert "c.png" in assets


def test_affected_by_transitive(graph):
    affected = graph.affected_by("c.png")
    assert "a.png" in affected
    assert "b.png" in affected


def test_affected_by_direct_only():
    g = DependencyGraph()
    g.add("x.js", ["y.js"])
    g.add("z.js", [])
    assert g.affected_by("y.js") == ["x.js"]


def test_remove_cleans_both_directions(graph):
    graph.remove("b.png")
    assert "b.png" not in graph.all_assets()
    assert "b.png" not in graph.dependents("c.png")


def test_add_new_dependency():
    g = DependencyGraph()
    g.add("main.css", ["reset.css"])
    assert g.dependencies("main.css") == ["reset.css"]
    assert g.dependents("reset.css") == ["main.css"]


def test_affected_by_no_dependents():
    g = DependencyGraph()
    g.add("solo.png", [])
    assert g.affected_by("solo.png") == []
