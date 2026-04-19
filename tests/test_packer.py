"""Tests for assetpacker.packer module."""

import os
import zipfile

import pytest

from assetpacker.config import PackerConfig
from assetpacker.optimizer import OptimizeResult, OptimizeSummary
from assetpacker.packer import pack, pack_to_folder, pack_to_zip


@pytest.fixture
def config(tmp_path):
    cfg = PackerConfig()
    cfg.output_dir = str(tmp_path / "output")
    return cfg


@pytest.fixture
def summary(tmp_path):
    out_dir = tmp_path / "output"
    out_dir.mkdir(parents=True)
    files = []
    for name in ["sprite.png", "music.ogg", "font.woff2"]:
        p = out_dir / name
        p.write_bytes(b"data" * 64)
        files.append(OptimizeResult(
            input_path=str(tmp_path / name),
            output_path=str(p),
            original_bytes=512,
            optimized_bytes=256,
        ))
    return OptimizeSummary(results=files)


def test_pack_to_zip_creates_file(summary, config):
    result = pack_to_zip(summary, config)
    assert os.path.isfile(result.output_path)
    assert result.output_path.endswith(".zip")


def test_pack_to_zip_contains_all_files(summary, config):
    result = pack_to_zip(summary, config)
    with zipfile.ZipFile(result.output_path) as zf:
        names = zf.namelist()
    assert len(names) == 3


def test_pack_to_zip_files_packed_count(summary, config):
    result = pack_to_zip(summary, config)
    assert result.files_packed == 3


def test_pack_to_folder_creates_directory(summary, config):
    result = pack_to_folder(summary, config)
    assert os.path.isdir(result.output_path)


def test_pack_to_folder_files_packed_count(summary, config):
    result = pack_to_folder(summary, config)
    assert result.files_packed == 3


def test_pack_missing_file_records_error(summary, config):
    summary.results[0].output_path = "/nonexistent/ghost.png"
    result = pack_to_zip(summary, config)
    assert len(result.errors) == 1
    assert "ghost.png" in result.errors[0]


def test_pack_success_flag(summary, config):
    result = pack(summary, config)
    assert result.success is True


def test_pack_bundle_size_nonzero(summary, config):
    result = pack(summary, config)
    assert result.bundle_size_bytes > 0
    assert result.bundle_size_kb > 0
