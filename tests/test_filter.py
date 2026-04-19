"""Tests for assetpacker.filter module."""

import pytest
from pathlib import Path

from assetpacker.scanner import AssetManifest
from assetpacker.filter import FilterConfig, apply_filter, describe_filter, _matches_any


@pytest.fixture
def manifest(tmp_path):
    def make(rel):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x")
        return p

    return AssetManifest(
        images=[make("img/hero.png"), make("img/bg.jpg")],
        audio=[make("sfx/jump.wav")],
        fonts=[make("fonts/main.ttf")],
        other=[make("data/level.json")],
    )


def test_filter_config_from_dict():
    cfg = FilterConfig.from_dict({"include": ["*.png"], "exclude": ["*.tmp"]})
    assert cfg.include == ["*.png"]
    assert cfg.exclude == ["*.tmp"]


def test_filter_config_defaults():
    cfg = FilterConfig()
    assert cfg.include == []
    assert cfg.exclude == []


def test_matches_any_by_name():
    p = Path("assets/hero.png")
    assert _matches_any(p, ["*.png"])
    assert not _matches_any(p, ["*.jpg"])


def test_apply_filter_no_rules_returns_all(manifest):
    cfg = FilterConfig()
    result = apply_filter(manifest, cfg)
    assert len(result.all_assets()) == len(manifest.all_assets())


def test_apply_filter_include_png(manifest):
    cfg = FilterConfig(include=["*.png"])
    result = apply_filter(manifest, cfg)
    assert all(f.suffix == ".png" for f in result.all_assets())
    assert len(result.all_assets()) == 1


def test_apply_filter_exclude_wav(manifest):
    cfg = FilterConfig(exclude=["*.wav"])
    result = apply_filter(manifest, cfg)
    names = [f.name for f in result.all_assets()]
    assert "jump.wav" not in names


def test_apply_filter_include_and_exclude(manifest):
    cfg = FilterConfig(include=["*.png", "*.jpg"], exclude=["bg.jpg"])
    result = apply_filter(manifest, cfg)
    names = [f.name for f in result.all_assets()]
    assert "hero.png" in names
    assert "bg.jpg" not in names


def test_describe_filter_no_rules():
    cfg = FilterConfig()
    assert describe_filter(cfg) == "FilterConfig(no rules)"


def test_describe_filter_with_rules():
    cfg = FilterConfig(include=["*.png"], exclude=["*.tmp"])
    desc = describe_filter(cfg)
    assert "include" in desc
    assert "exclude" in desc
