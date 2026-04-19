"""Tests for assetpacker.cache."""

import json
import pytest
from pathlib import Path

from assetpacker.cache import BuildCache, CacheEntry, _hash_file


@pytest.fixture
def asset_file(tmp_path):
    f = tmp_path / "sprite.png"
    f.write_bytes(b"fakepng" * 10)
    return f


@pytest.fixture
def cache_file(tmp_path):
    return tmp_path / ".assetcache"


def test_new_file_is_changed(asset_file):
    cache = BuildCache()
    assert cache.is_changed(asset_file) is True


def test_updated_file_not_changed(asset_file):
    cache = BuildCache()
    cache.update(asset_file)
    assert cache.is_changed(asset_file) is False


def test_modified_file_is_changed(asset_file):
    cache = BuildCache()
    cache.update(asset_file)
    asset_file.write_bytes(b"different content")
    assert cache.is_changed(asset_file) is True


def test_remove_entry(asset_file):
    cache = BuildCache()
    cache.update(asset_file)
    cache.remove(asset_file)
    assert cache.is_changed(asset_file) is True


def test_save_and_load_roundtrip(asset_file, cache_file):
    cache = BuildCache()
    cache.update(asset_file)
    cache.save(cache_file)

    loaded = BuildCache.load(cache_file)
    assert not loaded.is_changed(asset_file)


def test_load_missing_file_returns_empty(cache_file):
    cache = BuildCache.load(cache_file)
    assert cache.entries == {}


def test_load_corrupt_file_returns_empty(cache_file):
    cache_file.write_text("not json{{")
    cache = BuildCache.load(cache_file)
    assert cache.entries == {}


def test_load_wrong_version_returns_empty(cache_file):
    cache_file.write_text(json.dumps({"version": 99, "entries": {}}))
    cache = BuildCache.load(cache_file)
    assert cache.entries == {}


def test_entry_stores_size(asset_file):
    cache = BuildCache()
    cache.update(asset_file)
    entry = cache.entries[str(asset_file)]
    assert entry.size == asset_file.stat().st_size
