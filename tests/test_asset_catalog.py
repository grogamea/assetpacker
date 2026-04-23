"""Tests for assetpacker.asset_catalog."""

import pytest
from pathlib import Path

from assetpacker.scanner import AssetManifest
from assetpacker.asset_catalog import (
    CatalogEntry,
    AssetCatalog,
    build_catalog,
)


@pytest.fixture
def asset_tree(tmp_path):
    (tmp_path / "hero.png").write_bytes(b"\x89PNG" + b"x" * 100)
    (tmp_path / "bg.jpg").write_bytes(b"\xff\xd8" + b"x" * 200)
    (tmp_path / "theme.ogg").write_bytes(b"OggS" + b"x" * 300)
    (tmp_path / "ui.ttf").write_bytes(b"\x00\x01\x00\x00" + b"x" * 50)
    (tmp_path / "levels.json").write_bytes(b"{\"levels\": []}")
    return tmp_path


@pytest.fixture
def manifest(asset_tree):
    return AssetManifest(
        images=[asset_tree / "hero.png", asset_tree / "bg.jpg"],
        audio=[asset_tree / "theme.ogg"],
        fonts=[asset_tree / "ui.ttf"],
        data=[asset_tree / "levels.json"],
        other=[],
    )


@pytest.fixture
def catalog(manifest):
    return build_catalog(manifest)


def test_catalog_total(catalog):
    assert catalog.total == 5


def test_catalog_by_category_images(catalog):
    images = catalog.by_category("images")
    assert len(images) == 2
    assert all(e.category == "images" for e in images)


def test_catalog_by_category_audio(catalog):
    audio = catalog.by_category("audio")
    assert len(audio) == 1
    assert audio[0].suffix == ".ogg"


def test_catalog_by_suffix(catalog):
    pngs = catalog.by_suffix(".png")
    assert len(pngs) == 1
    assert pngs[0].stem == "hero"


def test_catalog_by_suffix_no_dot(catalog):
    jpgs = catalog.by_suffix("jpg")
    assert len(jpgs) == 1
    assert jpgs[0].stem == "bg"


def test_catalog_find_by_stem(catalog):
    entry = catalog.find_by_stem("ui")
    assert entry is not None
    assert entry.category == "fonts"


def test_catalog_find_by_stem_missing(catalog):
    assert catalog.find_by_stem("nonexistent") is None


def test_catalog_categories(catalog):
    cats = catalog.categories()
    assert "images" in cats
    assert "audio" in cats
    assert "fonts" in cats
    assert cats == sorted(cats)


def test_catalog_entry_size(catalog):
    entry = catalog.find_by_stem("hero")
    assert entry is not None
    assert entry.size_bytes > 0


def test_catalog_to_dict(catalog):
    d = catalog.to_dict()
    assert d["total"] == 5
    assert isinstance(d["entries"], list)
    assert "categories" in d


def test_entry_to_dict(catalog):
    entry = catalog.find_by_stem("levels")
    assert entry is not None
    d = entry.to_dict()
    assert d["category"] == "data"
    assert d["stem"] == "levels"
    assert d["suffix"] == ".json"
