import json
from pathlib import Path
from assetpacker.asset_validator import ValidationResult


def report_text(result: ValidationResult) -> str:
    lines = []
    if result.valid:
        lines.append("Validation passed.")
    else:
        lines.append("Validation FAILED.")
    lines.append(result.summary())
    if result.errors:
        lines.append("\nErrors:")
        for issue in result.errors:
            lines.append(f"  {issue}")
    if result.warnings:
        lines.append("\nWarnings:")
        for issue in result.warnings:
            lines.append(f"  {issue}")
    return "\n".join(lines)


def report_json(result: ValidationResult) -> str:
    data = {
        "valid": result.valid,
        "summary": result.summary(),
        "errors": [
            {"path": str(i.path), "message": i.message}
            for i in result.errors
        ],
        "warnings": [
            {"path": str(i.path), "message": i.message}
            for i in result.warnings
        ],
    }
    return json.dumps(data, indent=2)


def write_report(result: ValidationResult, output: Path, fmt: str = "text") -> None:
    if fmt == "json":
        content = report_json(result)
    else:
        content = report_text(result)
    output.write_text(content, encoding="utf-8")
