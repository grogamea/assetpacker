"""Tests for assetpacker.optimizer module."""

import pytest
from pathlib import Path

from assetpacker.config import PackerConfig
from assetpacker.scanner import AssetManifest, scan_directory
from assetpacker.optimizer import optimize, OptimizeResult, OptimizeSummary


@pytest.fixture
def asset_tree(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    (images / "hero.png").write_bytes(b"PNG" + b"\x00" * 97)
    (images / "bg.jpg").write_bytes(b"JPG" + b"\x00" * 197)

    audio = tmp_path / "audio"
    audio.mkdir()
    (audio / "theme.ogg").write_bytes(b"OGG" + b"\x00" * 49)

    return tmp_path


@pytest.fixture
def config(asset_tree):
    return PackerConfig(input_dir=asset_tree, targets=["web"])


@pytest.fixture
def manifest(asset_tree):
    return scan_directory(asset_tree)


def test_optimize_returns_summary(manifest, config, tmp_path):
    out = tmp_path / "out"
    result = optimize(manifest, config, out)
    assert isinstance(result, OptimizeSummary)


def test_optimize_copies_all_assets(manifest, config, tmp_path):
    out = tmp_path / "out"
    result = optimize(manifest, config, out)
    assert len(result.results) == len(manifest.all_assets())


def test_optimize_output_files_exist(manifest, config, tmp_path):
    out = tmp_path / "out"
    optimize(manifest, config, out)
    assert (out / "images" / "hero.png").exists()
    assert (out / "audio" / "theme.ogg").exists()


def test_optimize_result_sizes(manifest, config, tmp_path):
    out = tmp_path / "out"
    summary = optimize(manifest, config, out)
    for r in summary.results:
        assert r.original_size > 0
        assert r.optimized_size > 0


def test_optimize_summary_totals(manifest, config, tmp_path):
    out = tmp_path / "out"
    summary = optimize(manifest, config, out)
    assert summary.total_original > 0
    assert summary.total_optimized > 0
    assert summary.error_count == 0
    assert summary.skipped_count == 0


def test_savings_pct_zero_size():
    r = OptimizeResult(
        source=Path("a"),
        dest=Path("b"),
        original_size=0,
        optimized_size=0,
    )
    assert r.savings_pct == 0.0


def test_savings_pct_positive():
    r = OptimizeResult(
        source=Path("a"),
        dest=Path("b"),
        original_size=200,
        optimized_size=150,
    )
    assert r.savings_pct == pytest.approx(25.0)
