"""Tests for assetpacker.lint_reporter."""
import json
from pathlib import Path

import pytest

from assetpacker.asset_linter import LintIssue, LintResult
from assetpacker.lint_reporter import report_json, report_text, write_report


@pytest.fixture()
def clean_result() -> LintResult:
    return LintResult()


@pytest.fixture()
def mixed_result() -> LintResult:
    return LintResult(issues=[
        LintIssue("bad file.png", "spaces-in-name", "has spaces", "error"),
        LintIssue("sprite__idle.png", "double-underscore", "double __", "warning"),
    ])


# ---------------------------------------------------------------------------
# report_text
# ---------------------------------------------------------------------------

def test_report_text_clean_message(clean_result):
    text = report_text(clean_result)
    assert "clean" in text.lower() or "no lint" in text.lower()


def test_report_text_contains_issue_codes(mixed_result):
    text = report_text(mixed_result)
    assert "spaces-in-name" in text
    assert "double-underscore" in text


def test_report_text_contains_summary(mixed_result):
    text = report_text(mixed_result)
    assert "error" in text.lower()
    assert "warning" in text.lower()


# ---------------------------------------------------------------------------
# report_json
# ---------------------------------------------------------------------------

def test_report_json_is_valid_json(mixed_result):
    raw = report_json(mixed_result)
    data = json.loads(raw)
    assert isinstance(data, dict)


def test_report_json_passed_false_on_errors(mixed_result):
    data = json.loads(report_json(mixed_result))
    assert data["passed"] is False


def test_report_json_passed_true_when_clean(clean_result):
    data = json.loads(report_json(clean_result))
    assert data["passed"] is True


def test_report_json_errors_list(mixed_result):
    data = json.loads(report_json(mixed_result))
    assert len(data["errors"]) == 1
    assert data["errors"][0]["code"] == "spaces-in-name"


def test_report_json_warnings_list(mixed_result):
    data = json.loads(report_json(mixed_result))
    assert len(data["warnings"]) == 1


# ---------------------------------------------------------------------------
# write_report
# ---------------------------------------------------------------------------

def test_write_report_text_creates_file(tmp_path, mixed_result):
    out = tmp_path / "lint_report.txt"
    write_report(mixed_result, out, fmt="text")
    assert out.exists()


def test_write_report_json_creates_file(tmp_path, mixed_result):
    out = tmp_path / "reports" / "lint.json"
    write_report(mixed_result, out, fmt="json")
    assert out.exists()
    data = json.loads(out.read_text())
    assert "passed" in data
