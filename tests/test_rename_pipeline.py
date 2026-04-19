import pytest
from pathlib import Path
from assetpacker.asset_renamer import RenameRule
from assetpacker.rename_pipeline import run_rename_pipeline, RenamePipelineResult


@pytest.fixture
def asset_tree(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    files = []
    for name, data in [("bg.png", b"img"), ("music.ogg", b"audio"), ("ui.ttf", b"font")]:
        f = src / name
        f.write_bytes(data)
        files.append(f)
    return files, tmp_path / "out"


def test_pipeline_copies_files(asset_tree):
    files, out = asset_tree
    rule = RenameRule(pattern="prefix", prefix="game_")
    result = run_rename_pipeline(files, out, rule, copy=True)
    assert result.success
    copied = list(out.iterdir())
    assert len(copied) == 3


def test_pipeline_prefixed_names(asset_tree):
    files, out = asset_tree
    rule = RenameRule(pattern="prefix", prefix="v1_")
    result = run_rename_pipeline(files, out, rule, copy=True)
    for f in out.iterdir():
        assert f.name.startswith("v1_")


def test_pipeline_no_copy_does_not_create_files(asset_tree):
    files, out = asset_tree
    rule = RenameRule(pattern="prefix", prefix="x_")
    result = run_rename_pipeline(files, out, rule, copy=False)
    assert result.success
    assert not out.exists()


def test_pipeline_rename_map_populated(asset_tree):
    files, out = asset_tree
    rule = RenameRule(pattern="prefix", prefix="p_")
    result = run_rename_pipeline(files, out, rule, copy=False)
    rmap = result.rename_map
    assert len(rmap) == 3
    for v in rmap.values():
        assert "p_" in v


def test_pipeline_hash_rename(asset_tree):
    files, out = asset_tree
    rule = RenameRule(pattern="hash", hash_length=6)
    result = run_rename_pipeline(files, out, rule, copy=True)
    assert result.success
    assert len(list(out.iterdir())) == 3


def test_pipeline_result_success_no_errors(asset_tree):
    files, out = asset_tree
    rule = RenameRule(pattern="flatten")
    result = run_rename_pipeline(files, out, rule, copy=True)
    assert result.errors == []
    assert result.success
