"""Format and write lint results to various outputs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from assetpacker.asset_linter import LintResult


def report_text(result: LintResult) -> str:
    """Return a human-readable text report."""
    if not result.issues:
        return "No lint issues found. All assets look clean."

    lines = ["Lint Report", "=" * 40]
    for issue in sorted(result.issues, key=lambda i: (i.severity, i.path)):
        lines.append(str(issue))
    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def report_json(result: LintResult) -> str:
    """Return a JSON-formatted lint report."""
    data = {
        "passed": result.passed,
        "summary": result.summary(),
        "errors": [
            {"path": i.path, "code": i.code, "message": i.message}
            for i in result.errors
        ],
        "warnings": [
            {"path": i.path, "code": i.code, "message": i.message}
            for i in result.warnings
        ],
    }
    return json.dumps(data, indent=2)


def write_report(
    result: LintResult,
    output_path: Path,
    fmt: Literal["text", "json"] = "text",
) -> None:
    """Write a lint report to a file."""
    content = report_json(result) if fmt == "json" else report_text(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
