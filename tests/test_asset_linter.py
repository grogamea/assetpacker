"""Tests for assetpacker.asset_linter."""
from pathlib import Path

import pytest

from assetpacker.asset_linter import LintIssue, LintResult, lint_paths


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paths(*names: str) -> list[Path]:
    return [Path(n) for n in names]


# ---------------------------------------------------------------------------
# LintIssue
# ---------------------------------------------------------------------------

def test_lint_issue_str_contains_code():
    issue = LintIssue(path="a/b.png", code="spaces-in-name", message="has spaces", severity="error")
    assert "spaces-in-name" in str(issue)


def test_lint_issue_str_contains_severity():
    issue = LintIssue(path="a/b.png", code="no-extension", message="no ext", severity="error")
    assert "ERROR" in str(issue)


# ---------------------------------------------------------------------------
# LintResult
# ---------------------------------------------------------------------------

def test_lint_result_passed_when_no_errors():
    result = LintResult(issues=[
        LintIssue("a.png", "double-underscore", "msg", "warning")
    ])
    assert result.passed is True


def test_lint_result_fails_when_errors_present():
    result = LintResult(issues=[
        LintIssue("bad file.png", "spaces-in-name", "msg", "error")
    ])
    assert result.passed is False


def test_lint_result_errors_filters_correctly():
    result = LintResult(issues=[
        LintIssue("a.png", "c1", "m", "error"),
        LintIssue("b.png", "c2", "m", "warning"),
    ])
    assert len(result.errors) == 1
    assert len(result.warnings) == 1


def test_lint_result_summary_contains_counts():
    result = LintResult(issues=[
        LintIssue("a.png", "c1", "m", "error"),
        LintIssue("b.png", "c2", "m", "warning"),
    ])
    assert "1 error" in result.summary()
    assert "1 warning" in result.summary()


# ---------------------------------------------------------------------------
# lint_paths rules
# ---------------------------------------------------------------------------

def test_spaces_in_name_is_error():
    result = lint_paths(_paths("assets/bad file.png"))
    codes = [i.code for i in result.issues]
    assert "spaces-in-name" in codes
    assert any(i.severity == "error" for i in result.issues if i.code == "spaces-in-name")


def test_uppercase_extension_is_warning():
    result = lint_paths(_paths("assets/sprite.PNG"))
    codes = [i.code for i in result.issues]
    assert "uppercase-ext" in codes


def test_no_extension_is_error():
    result = lint_paths(_paths("assets/noext"))
    codes = [i.code for i in result.issues]
    assert "no-extension" in codes


def test_double_underscore_is_warning():
    result = lint_paths(_paths("assets/sprite__idle.png"))
    codes = [i.code for i in result.issues]
    assert "double-underscore" in codes


def test_clean_path_has_no_issues():
    result = lint_paths(_paths("assets/sprites/hero_idle.png"))
    assert result.issues == []
    assert result.passed is True


def test_deep_nesting_warning():
    result = lint_paths(_paths("a/b/c/d/e/f/g/sprite.png"))
    codes = [i.code for i in result.issues]
    assert "deep-nesting" in codes
