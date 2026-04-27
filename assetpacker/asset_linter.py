"""Lint asset names and paths for common issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from assetpacker.scanner import AssetManifest


@dataclass
class LintIssue:
    path: str
    code: str
    message: str
    severity: str = "warning"  # "warning" | "error"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.code}: {self.path} — {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        return (
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s) "
            f"across {len(self.issues)} issue(s)"
        )


_RULES = [
    ("spaces-in-name", "error", lambda p: " " in Path(p).name,
     "Filename contains spaces"),
    ("uppercase-ext", "warning", lambda p: Path(p).suffix != Path(p).suffix.lower(),
     "File extension is not lowercase"),
    ("deep-nesting", "warning", lambda p: len(Path(p).parts) > 6,
     "Path is deeply nested (> 6 levels)"),
    ("double-underscore", "warning", lambda p: "__" in Path(p).name,
     "Filename contains double underscore"),
    ("no-extension", "error", lambda p: Path(p).suffix == "",
     "File has no extension"),
]


def lint_manifest(manifest: AssetManifest) -> LintResult:
    """Run all lint rules against every asset in the manifest."""
    result = LintResult()
    for asset_path in manifest.all_assets():
        rel = str(asset_path)
        for code, severity, check, message in _RULES:
            if check(rel):
                result.issues.append(
                    LintIssue(path=rel, code=code, message=message, severity=severity)
                )
    return result


def lint_paths(paths: List[Path]) -> LintResult:
    """Run lint rules against an explicit list of paths."""
    result = LintResult()
    for path in paths:
        rel = str(path)
        for code, severity, check, message in _RULES:
            if check(rel):
                result.issues.append(
                    LintIssue(path=rel, code=code, message=message, severity=severity)
                )
    return result
