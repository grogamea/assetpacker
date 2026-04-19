"""Tests for tag_index module."""

import pytest
from unittest.mock import MagicMock
from assetpacker.tag_index import TagIndex, build_tag_index


@pytest.fixture
def index():
    idx = TagIndex()
    idx.add("images/hero.png", ["ui", "hero"])
    idx.add("images/bg.png", ["ui", "background"])
    idx.add("audio/theme.ogg", ["music", "loop"])
    return idx


def test_tags_for_asset(index):
    assert index.tags_for("images/hero.png") == {"ui", "hero"}


def test_assets_for_tag(index):
    assert index.assets_for_tag("ui") == {"images/hero.png", "images/bg.png"}


def test_all_tags_sorted(index):
    tags = index.all_tags()
    assert tags == sorted(tags)
    assert "ui" in tags
    assert "music" in tags


def test_remove_asset(index):
    index.remove("images/hero.png")
    assert "images/hero.png" not in index.assets_for_tag("ui")
    assert index.tags_for("images/hero.png") == set()


def test_remove_cleans_empty_tag(index):
    index.remove("audio/theme.ogg")
    assert "loop" not in index.all_tags()


def test_to_dict(index):
    d = index.to_dict()
    assert isinstance(d, dict)
    assert "ui" in d
    assert sorted(d["ui"]) == ["images/bg.png", "images/hero.png"]


def test_unknown_asset_returns_empty(index):
    assert index.tags_for("missing/file.png") == set()


def test_unknown_tag_returns_empty(index):
    assert index.assets_for_tag("nonexistent") == set()


def test_build_tag_index():
    manifest = MagicMock()
    manifest.all_assets.return_value = ["a.png", "b.png", "c.ogg"]
    tag_map = {"a.png": ["sprite"], "c.ogg": ["sfx"]}
    index = build_tag_index(manifest, tag_map)
    assert index.assets_for_tag("sprite") == {"a.png"}
    assert index.assets_for_tag("sfx") == {"c.ogg"}
    assert index.tags_for("b.png") == set()
