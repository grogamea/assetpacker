"""Tests for assetpacker.asset_sorter."""
import pytest
from pathlib import Path

from assetpacker.scanner import AssetManifest, scan_directory
from assetpacker.asset_sorter import sort_assets, describe_sort, SortedManifest


@pytest.fixture
def asset_tree(tmp_path):
    (tmp_path / "ui").mkdir()
    (tmp_path / "sfx").mkdir()
    (tmp_path / "fonts").mkdir()

    (tmp_path / "ui" / "button.png").write_bytes(b"x" * 200)
    (tmp_path / "ui" / "logo.png").write_bytes(b"x" * 800)
    (tmp_path / "sfx" / "click.ogg").write_bytes(b"x" * 400)
    (tmp_path / "fonts" / "main.ttf").write_bytes(b"x" * 100)
    (tmp_path / "data.bin").write_bytes(b"x" * 50)
    return tmp_path


@pytest.fixture
def manifest(asset_tree):
    return scan_directory(asset_tree)


def test_sort_returns_sorted_manifest(manifest):
    result = sort_assets(manifest)
    assert isinstance(result, SortedManifest)
    assert result.total == 5


def test_sort_fonts_come_first(manifest):
    result = sort_assets(manifest)
    first = result.assets[0]
    assert first.suffix == ".ttf"


def test_sort_audio_after_images(manifest):
    result = sort_assets(manifest)
    names = [p.name for p in result.assets]
    img_indices = [i for i, n in enumerate(names) if n.endswith(".png")]
    audio_indices = [i for i, n in enumerate(names) if n.endswith(".ogg")]
    assert max(img_indices) < min(audio_indices)


def test_sort_other_comes_last(manifest):
    result = sort_assets(manifest)
    last = result.assets[-1]
    assert last.name == "data.bin"


def test_sort_by_size_orders_within_category(manifest):
    result = sort_assets(manifest, by_size=True)
    png_assets = [p for p in result.assets if p.suffix == ".png"]
    sizes = [p.stat().st_size for p in png_assets]
    assert sizes == sorted(sizes)


def test_sort_reverse_puts_other_first(manifest):
    result = sort_assets(manifest, reverse=True)
    first = result.assets[0]
    assert first.name == "data.bin"


def test_position_of_returns_index(manifest):
    result = sort_assets(manifest)
    font = next(p for p in result.assets if p.suffix == ".ttf")
    assert result.position_of(font) == 0


def test_position_of_unknown_returns_none(manifest):
    result = sort_assets(manifest)
    assert result.position_of(Path("/nonexistent/file.xyz")) is None


def test_describe_sort_contains_counts(manifest):
    result = sort_assets(manifest)
    desc = describe_sort(result, manifest)
    assert "fonts: 1" in desc
    assert "images: 2" in desc
    assert "audio: 1" in desc
