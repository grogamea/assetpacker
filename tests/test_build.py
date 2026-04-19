"""Tests for assetpacker.build — BuildContext and run_build integration."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from assetpacker.build import BuildContext, run_build
from assetpacker.config import PackerConfig


@pytest.fixture
def config(tmp_path):
    return PackerConfig(
        source_dir=str(tmp_path / "assets"),
        output_dir=str(tmp_path / "dist"),
        target="web",
        compress=True,
        formats=["png", "mp3", "ttf"],
    )


@pytest.fixture
def asset_tree(tmp_path):
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "hero.png").write_bytes(b"PNG" + b"\x00" * 64)
    (assets / "theme.mp3").write_bytes(b"ID3" + b"\x00" * 128)
    (assets / "ui.ttf").write_bytes(b"\x00" * 32)
    return assets


def test_build_context_stores_config(config):
    ctx = BuildContext(config=config)
    assert ctx.config is config


def test_build_context_default_logger(config):
    from assetpacker.logger import BuildLogger
    ctx = BuildContext(config=config)
    assert isinstance(ctx.logger, BuildLogger)


def test_build_context_accepts_custom_logger(config):
    from assetpacker.logger import BuildLogger
    logger = BuildLogger()
    ctx = BuildContext(config=config, logger=logger)
    assert ctx.logger is logger


def test_run_build_returns_report(config, asset_tree, tmp_path):
    config.source_dir = str(asset_tree)
    config.output_dir = str(tmp_path / "dist")
    report = run_build(config)
    from assetpacker.reporter import BuildReport
    assert isinstance(report, BuildReport)


def test_run_build_creates_output(config, asset_tree, tmp_path):
    config.source_dir = str(asset_tree)
    out = tmp_path / "dist"
    config.output_dir = str(out)
    run_build(config)
    assert out.exists()


def test_run_build_report_has_files(config, asset_tree, tmp_path):
    config.source_dir = str(asset_tree)
    config.output_dir = str(tmp_path / "dist")
    report = run_build(config)
    assert report.total_files > 0


def test_run_build_logs_start(config, asset_tree, tmp_path):
    from assetpacker.logger import BuildLogger
    config.source_dir = str(asset_tree)
    config.output_dir = str(tmp_path / "dist")
    logger = BuildLogger()
    run_build(config, logger=logger)
    messages = [e.message for e in logger.entries]
    assert any("build" in m.lower() or "start" in m.lower() for m in messages)


def test_run_build_logs_completion(config, asset_tree, tmp_path):
    from assetpacker.logger import BuildLogger
    config.source_dir = str(asset_tree)
    config.output_dir = str(tmp_path / "dist")
    logger = BuildLogger()
    run_build(config, logger=logger)
    messages = [e.message for e in logger.entries]
    assert any("complete" in m.lower() or "done" in m.lower() or "finish" in m.lower() for m in messages)
