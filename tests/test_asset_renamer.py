import pytest
from pathlib import Path
from assetpacker.asset_renamer import (
    RenameRule,
    RenameResult,
    rename_assets,
    build_rename_map,
    describe_rename,
)


@pytest.fixture
def asset_tree(tmp_path):
    files = []
    for name in ["hero.png", "click.wav", "font.ttf"]:
        f = tmp_path / name
        f.write_bytes(b"data:" + name.encode())
        files.append(f)
    return files


def test_rename_hash_changes_name(asset_tree):
    rule = RenameRule(pattern="hash", hash_length=8)
    results = rename_assets(asset_tree, rule)
    for r in results:
        assert r.changed
        assert r.renamed.suffix == r.original.suffix
        assert r.original.stem in r.renamed.stem or len(r.renamed.stem) > len(r.original.stem)


def test_rename_prefix_prepends(asset_tree):
    rule = RenameRule(pattern="prefix", prefix="game_")
    results = rename_assets(asset_tree, rule)
    for r in results:
        assert r.renamed.name.startswith("game_")
        assert r.changed


def test_rename_flatten_removes_parents(asset_tree):
    rule = RenameRule(pattern="flatten")
    results = rename_assets(asset_tree, rule)
    for r in results:
        assert str(r.renamed.parent) == "."


def test_rename_noop_pattern(asset_tree):
    rule = RenameRule(pattern="noop")
    results = rename_assets(asset_tree, rule)
    for r in results:
        assert not r.changed


def test_build_rename_map_excludes_unchanged(asset_tree):
    rule = RenameRule(pattern="prefix", prefix="p_")
    results = rename_assets(asset_tree, rule)
    mapping = build_rename_map(results)
    assert len(mapping) == len(asset_tree)
    for k, v in mapping.items():
        assert Path(v).name.startswith("p_")


def test_build_rename_map_empty_when_no_change(asset_tree):
    rule = RenameRule(pattern="noop")
    results = rename_assets(asset_tree, rule)
    mapping = build_rename_map(results)
    assert mapping == {}


def test_describe_rename_contains_count(asset_tree):
    rule = RenameRule(pattern="prefix", prefix="x_")
    results = rename_assets(asset_tree, rule)
    desc = describe_rename(results)
    assert "3/3" in desc


def test_rename_result_changed_property(asset_tree):
    p = asset_tree[0]
    r_changed = RenameResult(original=p, renamed=p.with_name("new.png"))
    r_same = RenameResult(original=p, renamed=p)
    assert r_changed.changed
    assert not r_same.changed
