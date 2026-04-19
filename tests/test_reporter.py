"""Tests for assetpacker.reporter."""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from assetpacker.reporter import BuildReport, generate_report, save_report


@pytest.fixture
def optimize_summary():
    s = MagicMock()
    s.total_original = 204800   # 200 KB
    s.total_optimized = 153600  # 150 KB
    s.overall_savings_pct = 25.0
    return s


@pytest.fixture
def pack_result(tmp_path):
    r = MagicMock()
    r.files_packed = 12
    r.output_path = tmp_path / "out.zip"
    return r


@pytest.fixture
def report(optimize_summary, pack_result):
    return generate_report("web", optimize_summary, pack_result, warnings=["missing icon"])


def test_report_has_timestamp(report):
    assert report.timestamp.endswith("Z")
    assert "T" in report.timestamp


def test_report_total_files(report, pack_result):
    assert report.total_files == pack_result.files_packed


def test_report_to_dict_keys(report):
    d = report.to_dict()
    for key in ("timestamp", "target", "total_files", "original_size_kb",
                "optimized_size_kb", "savings_pct", "output_path", "warnings"):
        assert key in d


def test_report_to_dict_values(report):
    d = report.to_dict()
    assert d["target"] == "web"
    assert d["total_files"] == 12
    assert d["original_size_kb"] == 200.0
    assert d["optimized_size_kb"] == 150.0
    assert d["savings_pct"] == 25.0
    assert d["warnings"] == ["missing icon"]


def test_report_to_json_valid(report):
    raw = report.to_json()
    parsed = json.loads(raw)
    assert parsed["target"] == "web"


def test_report_to_text_contains_info(report):
    text = report.to_text()
    assert "web" in text
    assert "200.0 KB" in text
    assert "missing icon" in text


def test_save_report_writes_file(report, tmp_path):
    out = tmp_path / "report.json"
    save_report(report, str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["target"] == "web"


def test_generate_report_no_warnings(optimize_summary, pack_result):
    r = generate_report("desktop", optimize_summary, pack_result)
    assert r.warnings == []
