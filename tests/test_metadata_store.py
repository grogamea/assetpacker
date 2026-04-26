"""Tests for assetpacker.metadata_store."""
import json
from pathlib import Path

import pytest

from assetpacker.asset_metadata import extract_metadata
from assetpacker.metadata_store import MetadataStore, build_store


@pytest.fixture()
def asset_tree(tmp_path: Path):
    (tmp_path / "hero.png").write_bytes(b"PNG" * 80)
    (tmp_path / "theme.mp3").write_bytes(b"ID3" * 160)
    (tmp_path / "ui.ttf").write_bytes(b"TTF" * 40)
    return tmp_path


@pytest.fixture()
def store(asset_tree):
    return build_store([
        asset_tree / "hero.png",
        asset_tree / "theme.mp3",
        asset_tree / "ui.ttf",
    ])


def test_build_store_has_all_entries(store):
    assert len(store.all()) == 3


def test_store_get_returns_metadata(store, asset_tree):
    meta = store.get(asset_tree / "hero.png")
    assert meta is not None
    assert meta.extension == "png"


def test_store_get_missing_returns_none(store, tmp_path):
    assert store.get(tmp_path / "ghost.png") is None


def test_store_by_category_images(store):
    images = store.by_category("image")
    assert len(images) == 1
    assert images[0].extension == "png"


def test_store_categories_sorted(store):
    cats = store.categories()
    assert cats == sorted(cats)
    assert "image" in cats
    assert "audio" in cats
    assert "font" in cats


def test_store_remove(store, asset_tree):
    store.remove(asset_tree / "hero.png")
    assert store.get(asset_tree / "hero.png") is None
    assert len(store.all()) == 2


def test_store_save_creates_file(store, tmp_path):
    dest = tmp_path / "meta" / "metadata.json"
    store.save(dest)
    assert dest.exists()


def test_store_save_valid_json(store, tmp_path):
    dest = tmp_path / "metadata.json"
    store.save(dest)
    data = json.loads(dest.read_text())
    assert isinstance(data, list)
    assert len(data) == 3


def test_store_load_roundtrip(store, tmp_path):
    dest = tmp_path / "metadata.json"
    store.save(dest)
    loaded = MetadataStore.load(dest)
    assert len(loaded.all()) == len(store.all())


def test_store_load_preserves_category(store, asset_tree, tmp_path):
    dest = tmp_path / "metadata.json"
    store.save(dest)
    loaded = MetadataStore.load(dest)
    orig = store.get(asset_tree / "hero.png")
    restored = loaded.get(asset_tree / "hero.png")
    assert restored is not None
    assert restored.category == orig.category


def test_store_load_missing_file_returns_empty(tmp_path):
    store = MetadataStore.load(tmp_path / "nonexistent.json")
    assert store.all() == []
