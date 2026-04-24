"""Tests for assetpacker.asset_diff."""

import time
import pytest
from pathlib import Path
from assetpacker.scanner import scan_directory
from assetpacker.asset_diff import diff_manifests, describe_diff, DiffResult


@pytest.fixture
def asset_tree(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "audio").mkdir()
    (tmp_path / "images" / "hero.png").write_bytes(b"PNG" * 10)
    (tmp_path / "images" / "bg.png").write_bytes(b"PNG" * 8)
    (tmp_path / "audio" / "theme.ogg").write_bytes(b"OGG" * 20)
    return tmp_path


def test_diff_no_changes(asset_tree):
    manifest_a = scan_directory(asset_tree)
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    assert not result.has_changes
    assert result.total_changes == 0


def test_diff_detects_added(asset_tree):
    manifest_a = scan_directory(asset_tree)
    (asset_tree / "images" / "new.png").write_bytes(b"PNG" * 5)
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    assert any("new.png" in p for p in result.added)
    assert result.has_changes


def test_diff_detects_removed(asset_tree):
    manifest_a = scan_directory(asset_tree)
    (asset_tree / "audio" / "theme.ogg").unlink()
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    assert any("theme.ogg" in p for p in result.removed)


def test_diff_detects_modified(asset_tree):
    manifest_a = scan_directory(asset_tree)
    target = asset_tree / "images" / "hero.png"
    time.sleep(0.05)
    target.write_bytes(b"PNG" * 99)
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    assert any("hero.png" in p for p in result.changed)


def test_diff_result_to_dict(asset_tree):
    manifest_a = scan_directory(asset_tree)
    (asset_tree / "images" / "extra.png").write_bytes(b"PNG")
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    d = result.to_dict()
    assert "added" in d
    assert "removed" in d
    assert "changed" in d
    assert "total_changes" in d
    assert isinstance(d["added"], list)


def test_diff_summary_no_changes(asset_tree):
    manifest_a = scan_directory(asset_tree)
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    assert result.summary() == "no changes"


def test_diff_summary_with_changes(asset_tree):
    manifest_a = scan_directory(asset_tree)
    (asset_tree / "images" / "new.png").write_bytes(b"PNG")
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    assert "added" in result.summary()


def test_describe_diff_no_changes(asset_tree):
    manifest_a = scan_directory(asset_tree)
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    text = describe_diff(result)
    assert "No changes" in text


def test_describe_diff_with_changes(asset_tree):
    manifest_a = scan_directory(asset_tree)
    (asset_tree / "images" / "new.png").write_bytes(b"PNG")
    manifest_b = scan_directory(asset_tree)
    result = diff_manifests(manifest_a, manifest_b)
    text = describe_diff(result)
    assert "+" in text
    assert "new.png" in text
