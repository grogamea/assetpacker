"""Tests for assetpacker.asset_tagger."""
from pathlib import Path

import pytest

from assetpacker.scanner import AssetManifest
from assetpacker.asset_tagger import tag_assets, TaggerResult, TaggedAsset


@pytest.fixture()
def asset_tree(tmp_path: Path) -> Path:
    (tmp_path / "images").mkdir()
    (tmp_path / "audio").mkdir()
    (tmp_path / "fonts").mkdir()

    img = tmp_path / "images" / "hero.png"
    img.write_bytes(b"\x89PNG" + b"x" * 600 * 1024)  # large

    snd = tmp_path / "audio" / "click.wav"
    snd.write_bytes(b"RIFF" + b"x" * 100)  # small

    fnt = tmp_path / "fonts" / "main.ttf"
    fnt.write_bytes(b"x" * 60 * 1024)  # medium

    return tmp_path


@pytest.fixture()
def manifest(asset_tree: Path) -> AssetManifest:
    images = list((asset_tree / "images").glob("*"))
    audio = list((asset_tree / "audio").glob("*"))
    fonts = list((asset_tree / "fonts").glob("*"))
    return AssetManifest(assets={"images": images, "audio": audio, "fonts": fonts})


def test_tag_assets_returns_tagger_result(manifest: AssetManifest) -> None:
    result = tag_assets(manifest)
    assert isinstance(result, TaggerResult)


def test_total_matches_asset_count(manifest: AssetManifest) -> None:
    result = tag_assets(manifest)
    total_in_manifest = sum(len(v) for v in manifest.assets.values())
    assert result.total == total_in_manifest


def test_image_has_visual_tag(manifest: AssetManifest, asset_tree: Path) -> None:
    result = tag_assets(manifest)
    img_path = asset_tree / "images" / "hero.png"
    tags = result.tags_for(img_path)
    assert "visual" in tags


def test_audio_has_sound_tag(manifest: AssetManifest, asset_tree: Path) -> None:
    result = tag_assets(manifest)
    snd_path = asset_tree / "audio" / "click.wav"
    tags = result.tags_for(snd_path)
    assert "sound" in tags


def test_font_has_typography_tag(manifest: AssetManifest, asset_tree: Path) -> None:
    result = tag_assets(manifest)
    fnt_path = asset_tree / "fonts" / "main.ttf"
    tags = result.tags_for(fnt_path)
    assert "typography" in tags


def test_large_file_tagged_large(manifest: AssetManifest, asset_tree: Path) -> None:
    result = tag_assets(manifest)
    img_path = asset_tree / "images" / "hero.png"
    assert "large" in result.tags_for(img_path)


def test_small_file_tagged_small(manifest: AssetManifest, asset_tree: Path) -> None:
    result = tag_assets(manifest)
    snd_path = asset_tree / "audio" / "click.wav"
    assert "small" in result.tags_for(snd_path)


def test_medium_file_tagged_medium(manifest: AssetManifest, asset_tree: Path) -> None:
    result = tag_assets(manifest)
    fnt_path = asset_tree / "fonts" / "main.ttf"
    assert "medium" in result.tags_for(fnt_path)


def test_extra_rules_apply(manifest: AssetManifest, asset_tree: Path) -> None:
    rules = {"hero-asset": ["hero"]}
    result = tag_assets(manifest, extra_rules=rules)
    img_path = asset_tree / "images" / "hero.png"
    assert "hero-asset" in result.tags_for(img_path)


def test_extra_rules_do_not_apply_to_non_matching(manifest: AssetManifest, asset_tree: Path) -> None:
    rules = {"hero-asset": ["hero"]}
    result = tag_assets(manifest, extra_rules=rules)
    snd_path = asset_tree / "audio" / "click.wav"
    assert "hero-asset" not in result.tags_for(snd_path)


def test_all_tags_sorted(manifest: AssetManifest) -> None:
    result = tag_assets(manifest)
    tags = result.all_tags()
    assert tags == sorted(tags)


def test_assets_with_tag_filters_correctly(manifest: AssetManifest) -> None:
    result = tag_assets(manifest)
    visual_assets = result.assets_with_tag("visual")
    assert all("visual" in a.tags for a in visual_assets)
    assert len(visual_assets) >= 1


def test_tagged_asset_to_dict(manifest: AssetManifest, asset_tree: Path) -> None:
    result = tag_assets(manifest)
    img_path = asset_tree / "images" / "hero.png"
    asset = next(a for a in result.tagged if a.path == img_path)
    d = asset.to_dict()
    assert "path" in d
    assert "category" in d
    assert "tags" in d
    assert isinstance(d["tags"], list)
