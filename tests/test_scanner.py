"""Tests for assetpacker.scanner."""

from __future__ import annotations

import pytest
from pathlib import Path

from assetpacker.scanner import scan_directory, AssetManifest


@pytest.fixture()
def asset_tree(tmp_path: Path) -> Path:
    """Create a small fake asset directory tree."""
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "hero.png").write_bytes(b"")
    (tmp_path / "images" / "bg.jpg").write_bytes(b"")
    (tmp_path / "audio").mkdir()
    (tmp_path / "audio" / "theme.ogg").write_bytes(b"")
    (tmp_path / "fonts").mkdir()
    (tmp_path / "fonts" / "ui.ttf").write_bytes(b"")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "levels.json").write_bytes(b"{}")
    (tmp_path / "data" / "config.yaml").write_bytes(b"")
    (tmp_path / "misc").mkdir()
    (tmp_path / "misc" / "readme.txt").write_bytes(b"")
    return tmp_path


def test_scan_returns_manifest(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree)
    assert isinstance(manifest, AssetManifest)


def test_scan_categorizes_images(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree)
    names = {p.name for p in manifest.images}
    assert names == {"hero.png", "bg.jpg"}


def test_scan_categorizes_audio(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree)
    assert len(manifest.audio) == 1
    assert manifest.audio[0].name == "theme.ogg"


def test_scan_categorizes_fonts(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree)
    assert len(manifest.fonts) == 1


def test_scan_categorizes_data(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree)
    names = {p.name for p in manifest.data}
    assert names == {"levels.json", "config.yaml"}


def test_scan_unknown_files(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree)
    assert len(manifest.unknown) == 1
    assert manifest.unknown[0].name == "readme.txt"


def test_summary_totals(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree)
    summary = manifest.summary()
    assert summary["total"] == len(manifest.all_assets())
    assert summary["images"] == 2


def test_exclude_directory(asset_tree: Path) -> None:
    manifest = scan_directory(asset_tree, exclude=["audio"])
    assert all(p.name != "theme.ogg" for p in manifest.audio)


def test_missing_directory_raises() -> None:
    with pytest.raises(FileNotFoundError):
        scan_directory("/nonexistent/path/xyz")


def test_file_path_raises(tmp_path: Path) -> None:
    f = tmp_path / "file.txt"
    f.write_text("hello")
    with pytest.raises(NotADirectoryError):
        scan_directory(f)
