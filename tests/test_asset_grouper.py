import pytest
from pathlib import Path
from assetpacker.scanner import AssetManifest
from assetpacker.asset_grouper import (
    group_by_category,
    group_by_extension,
    group_by_prefix,
    describe_groups,
    GroupResult,
)


@pytest.fixture
def manifest():
    m = AssetManifest()
    m.categories = {
        "images": ["sprites/hero.png", "sprites/enemy.png", "ui/button.png"],
        "audio": ["sfx/jump.wav", "music/theme.ogg"],
        "fonts": ["fonts/main.ttf"],
    }
    return m


def test_group_by_category_returns_group_result(manifest):
    result = group_by_category(manifest)
    assert isinstance(result, GroupResult)


def test_group_by_category_names_match_categories(manifest):
    result = group_by_category(manifest)
    assert set(result.group_names) == {"images", "audio", "fonts"}


def test_group_by_category_counts(manifest):
    result = group_by_category(manifest)
    assert result.get("images").count == 3
    assert result.get("audio").count == 2
    assert result.get("fonts").count == 1


def test_group_by_category_total_assets(manifest):
    result = group_by_category(manifest)
    assert result.total_assets == 6


def test_group_by_extension(manifest):
    result = group_by_extension(manifest)
    assert "png" in result.group_names
    assert "wav" in result.group_names
    assert "ogg" in result.group_names
    assert "ttf" in result.group_names


def test_group_by_extension_png_count(manifest):
    result = group_by_extension(manifest)
    assert result.get("png").count == 3


def test_group_by_prefix(manifest):
    result = group_by_prefix(manifest)
    assert "sprites" in result.group_names
    assert "sfx" in result.group_names
    assert "music" in result.group_names
    assert "fonts" in result.group_names
    assert "ui" in result.group_names


def test_group_by_prefix_sprites_count(manifest):
    result = group_by_prefix(manifest)
    assert result.get("sprites").count == 2


def test_group_get_unknown_returns_none(manifest):
    result = group_by_category(manifest)
    assert result.get("nonexistent") is None


def test_to_dict_structure(manifest):
    result = group_by_category(manifest)
    d = result.to_dict()
    assert "images" in d
    assert d["images"]["count"] == 3
    assert isinstance(d["images"]["assets"], list)


def test_describe_groups_output(manifest):
    result = group_by_category(manifest)
    text = describe_groups(result)
    assert "Groups" in text
    assert "images" in text
    assert "audio" in text
