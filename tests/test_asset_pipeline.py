"""Tests for assetpacker.asset_pipeline — full pipeline orchestration."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from assetpacker.asset_pipeline import run_pipeline, PipelineResult
from assetpacker.config import PackerConfig
from assetpacker.scanner import AssetManifest
from assetpacker.filter import FilterConfig
from assetpacker.hooks import HookConfig
from assetpacker.optimizer import OptimizeSummary
from assetpacker.packer import PackResult
from assetpacker.reporter import BuildReport


def _make_manifest(n=3):
    m = MagicMock(spec=AssetManifest)
    m.total = n
    return m


def _make_opt_summary():
    s = MagicMock(spec=OptimizeSummary)
    s.results = []
    return s


def _make_pack_result(n=3):
    r = MagicMock(spec=PackResult)
    r.files_packed = n
    r.bundle_size_kb.return_value = 42.0
    return r


@pytest.fixture
def config():
    return PackerConfig()


@pytest.fixture
def dirs(tmp_path):
    src = tmp_path / "assets"
    src.mkdir()
    out = tmp_path / "dist"
    out.mkdir()
    return src, out


def _patch_pipeline(manifest=None, opt=None, pack=None):
    manifest = manifest or _make_manifest()
    opt = opt or _make_opt_summary()
    pack = pack or _make_pack_result()
    report = MagicMock(spec=BuildReport)
    return manifest, opt, pack, report


def test_pipeline_result_success_true(config, dirs):
    src, out = dirs
    manifest, opt, pack, report = _patch_pipeline()
    with patch("assetpacker.asset_pipeline.scan_directory", return_value=manifest), \
         patch("assetpacker.asset_pipeline.apply_filter", return_value=manifest), \
         patch("assetpacker.asset_pipeline.optimize_assets", return_value=opt), \
         patch("assetpacker.asset_pipeline.pack_to_folder", return_value=pack), \
         patch("assetpacker.asset_pipeline.BuildReport", return_value=report):
        result = run_pipeline(config, src, out)
    assert result.success is True


def test_pipeline_result_summary_contains_status(config, dirs):
    src, out = dirs
    manifest, opt, pack, report = _patch_pipeline()
    with patch("assetpacker.asset_pipeline.scan_directory", return_value=manifest), \
         patch("assetpacker.asset_pipeline.apply_filter", return_value=manifest), \
         patch("assetpacker.asset_pipeline.optimize_assets", return_value=opt), \
         patch("assetpacker.asset_pipeline.pack_to_folder", return_value=pack), \
         patch("assetpacker.asset_pipeline.BuildReport", return_value=report):
        result = run_pipeline(config, src, out)
    assert "OK" in result.summary() or "FAILED" in result.summary()


def test_pipeline_uses_zip_when_target_zip(config, dirs):
    src, out = dirs
    config.target = "zip"
    manifest, opt, pack, report = _patch_pipeline()
    with patch("assetpacker.asset_pipeline.scan_directory", return_value=manifest), \
         patch("assetpacker.asset_pipeline.apply_filter", return_value=manifest), \
         patch("assetpacker.asset_pipeline.optimize_assets", return_value=opt), \
         patch("assetpacker.asset_pipeline.pack_to_zip", return_value=pack) as mock_zip, \
         patch("assetpacker.asset_pipeline.BuildReport", return_value=report):
        run_pipeline(config, src, out)
    mock_zip.assert_called_once()


def test_pipeline_applies_filter(config, dirs):
    src, out = dirs
    manifest, opt, pack, report = _patch_pipeline()
    fc = FilterConfig(include=["*.png"])
    with patch("assetpacker.asset_pipeline.scan_directory", return_value=manifest), \
         patch("assetpacker.asset_pipeline.apply_filter", return_value=manifest) as mock_filter, \
         patch("assetpacker.asset_pipeline.optimize_assets", return_value=opt), \
         patch("assetpacker.asset_pipeline.pack_to_folder", return_value=pack), \
         patch("assetpacker.asset_pipeline.BuildReport", return_value=report):
        run_pipeline(config, src, out, filter_config=fc)
    mock_filter.assert_called_once()


def test_pipeline_result_has_report(config, dirs):
    src, out = dirs
    manifest, opt, pack, report = _patch_pipeline()
    with patch("assetpacker.asset_pipeline.scan_directory", return_value=manifest), \
         patch("assetpacker.asset_pipeline.apply_filter", return_value=manifest), \
         patch("assetpacker.asset_pipeline.optimize_assets", return_value=opt), \
         patch("assetpacker.asset_pipeline.pack_to_folder", return_value=pack), \
         patch("assetpacker.asset_pipeline.BuildReport", return_value=report):
        result = run_pipeline(config, src, out)
    assert result.report is report


def test_pipeline_zero_files_marks_failure(config, dirs):
    src, out = dirs
    manifest, opt, pack, report = _patch_pipeline(pack=_make_pack_result(0))
    with patch("assetpacker.asset_pipeline.scan_directory", return_value=manifest), \
         patch("assetpacker.asset_pipeline.apply_filter", return_value=manifest), \
         patch("assetpacker.asset_pipeline.optimize_assets", return_value=opt), \
         patch("assetpacker.asset_pipeline.pack_to_folder", return_value=pack), \
         patch("assetpacker.asset_pipeline.BuildReport", return_value=report):
        result = run_pipeline(config, src, out)
    assert result.success is False
