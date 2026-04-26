"""Tests for assetpacker.asset_metadata."""
from pathlib import Path

import pytest

from assetpacker.asset_metadata import (
    AssetMetadata,
    extract_all,
    extract_metadata,
    _infer_category,
)


@pytest.fixture()
def asset_tree(tmp_path: Path):
    files = {
        "hero.png": b"PNG" * 100,
        "theme.mp3": b"ID3" * 200,
        "ui.ttf": b"TTF" * 50,
        "levels.json": b'{"level": 1}',
        "blur.glsl": b"void main(){}" ,
        "readme.txt": b"notes",
    }
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
    return tmp_path


def test_extract_metadata_returns_asset_metadata(asset_tree):
    meta = extract_metadata(asset_tree / "hero.png")
    assert isinstance(meta, AssetMetadata)


def test_extract_metadata_correct_extension(asset_tree):
    meta = extract_metadata(asset_tree / "hero.png")
    assert meta.extension == "png"


def test_extract_metadata_correct_category_image(asset_tree):
    assert extract_metadata(asset_tree / "hero.png").category == "image"


def test_extract_metadata_correct_category_audio(asset_tree):
    assert extract_metadata(asset_tree / "theme.mp3").category == "audio"


def test_extract_metadata_correct_category_font(asset_tree):
    assert extract_metadata(asset_tree / "ui.ttf").category == "font"


def test_extract_metadata_correct_category_data(asset_tree):
    assert extract_metadata(asset_tree / "levels.json").category == "data"


def test_extract_metadata_correct_category_shader(asset_tree):
    assert extract_metadata(asset_tree / "blur.glsl").category == "shader"


def test_extract_metadata_other_category(asset_tree):
    assert extract_metadata(asset_tree / "readme.txt").category == "other"


def test_extract_metadata_size_bytes(asset_tree):
    path = asset_tree / "hero.png"
    meta = extract_metadata(path)
    assert meta.size_bytes == path.stat().st_size


def test_extract_metadata_size_kb(asset_tree):
    meta = extract_metadata(asset_tree / "hero.png")
    assert meta.size_kb == round(meta.size_bytes / 1024, 2)


def test_extract_metadata_tags_stored(asset_tree):
    meta = extract_metadata(asset_tree / "hero.png", tags=["ui", "hd"])
    assert meta.tags == ["ui", "hd"]


def test_extract_metadata_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_metadata(tmp_path / "ghost.png")


def test_extract_all_skips_missing(asset_tree):
    paths = [asset_tree / "hero.png", asset_tree / "ghost.png"]
    results = extract_all(paths)
    assert len(results) == 1


def test_to_dict_has_expected_keys(asset_tree):
    meta = extract_metadata(asset_tree / "hero.png")
    d = meta.to_dict()
    for key in ("path", "filename", "size_bytes", "size_kb", "extension", "category", "tags", "extra"):
        assert key in d
