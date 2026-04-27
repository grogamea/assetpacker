"""Tests for assetpacker.asset_scorer."""

import pytest
from pathlib import Path

from assetpacker.asset_scorer import (
    AssetScore,
    ScoredManifest,
    _compute_score,
    score_assets,
    describe_scores,
)
from assetpacker.scanner import AssetManifest


@pytest.fixture()
def asset_tree(tmp_path: Path) -> Path:
    (tmp_path / "font.ttf").write_bytes(b"f" * 100)
    (tmp_path / "sprite.png").write_bytes(b"p" * 2048)
    (tmp_path / "music.ogg").write_bytes(b"a" * 512 * 1024)  # 512 KB
    (tmp_path / "readme.txt").write_bytes(b"r" * 50)
    return tmp_path


@pytest.fixture()
def manifest(asset_tree: Path) -> AssetManifest:
    return AssetManifest(
        fonts=[asset_tree / "font.ttf"],
        images=[asset_tree / "sprite.png"],
        audio=[asset_tree / "music.ogg"],
        other=[asset_tree / "readme.txt"],
    )


def test_compute_score_font_is_highest():
    assert _compute_score("fonts", 100) > _compute_score("images", 100)


def test_compute_score_image_above_audio():
    assert _compute_score("images", 100) > _compute_score("audio", 100)


def test_compute_score_large_file_penalized():
    small = _compute_score("images", 100)
    large = _compute_score("images", 10 * 1024 * 1024)  # 10 MB
    assert small > large


def test_compute_score_never_negative():
    score = _compute_score("other", 999 * 1024 * 1024)
    assert score >= 0.0


def test_score_assets_returns_scored_manifest(manifest: AssetManifest):
    sm = score_assets(manifest)
    assert isinstance(sm, ScoredManifest)


def test_score_assets_total_matches_manifest(manifest: AssetManifest):
    sm = score_assets(manifest)
    total_in_manifest = (
        len(manifest.fonts)
        + len(manifest.images)
        + len(manifest.audio)
        + len(manifest.other)
    )
    assert sm.total == total_in_manifest


def test_score_assets_sorted_descending(manifest: AssetManifest):
    sm = score_assets(manifest)
    scores = [e.score for e in sm.entries]
    assert scores == sorted(scores, reverse=True)


def test_score_assets_font_ranked_first(manifest: AssetManifest):
    sm = score_assets(manifest)
    assert sm.entries[0].category == "fonts"


def test_scored_manifest_by_category(manifest: AssetManifest):
    sm = score_assets(manifest)
    images = sm.by_category("images")
    assert all(e.category == "images" for e in images)
    assert len(images) == 1


def test_scored_manifest_top_limits_results(manifest: AssetManifest):
    sm = score_assets(manifest)
    assert len(sm.top(2)) == 2


def test_asset_score_to_dict(manifest: AssetManifest):
    sm = score_assets(manifest)
    d = sm.entries[0].to_dict()
    assert "path" in d
    assert "score" in d
    assert "size_kb" in d
    assert "category" in d


def test_describe_scores_returns_string(manifest: AssetManifest):
    sm = score_assets(manifest)
    text = describe_scores(sm, top_n=2)
    assert isinstance(text, str)
    assert "top 2" in text
