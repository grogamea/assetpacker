from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

MAX_FILE_SIZES = {
    "image": 10 * 1024 * 1024,
    "audio": 50 * 1024 * 1024,
    "font": 2 * 1024 * 1024,
    "other": 20 * 1024 * 1024,
}

ALLOWED_EXTENSIONS = {
    "image": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"},
    "audio": {".mp3", ".ogg", ".wav", ".flac"},
    "font": {".ttf", ".otf", ".woff", ".woff2"},
}


@dataclass
class ValidationIssue:
    path: Path
    severity: str  # "error" | "warning"
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.path}: {self.message}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        return f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)"


def _categorize(path: Path) -> Optional[str]:
    ext = path.suffix.lower()
    for cat, exts in ALLOWED_EXTENSIONS.items():
        if ext in exts:
            return cat
    return "other"


def validate_assets(paths: List[Path]) -> ValidationResult:
    result = ValidationResult()
    for path in paths:
        if not path.exists():
            result.issues.append(ValidationIssue(path, "error", "File does not exist"))
            continue
        if not path.is_file():
            result.issues.append(ValidationIssue(path, "error", "Not a regular file"))
            continue
        category = _categorize(path)
        max_size = MAX_FILE_SIZES.get(category, MAX_FILE_SIZES["other"])
        size = path.stat().st_size
        if size == 0:
            result.issues.append(ValidationIssue(path, "warning", "File is empty"))
        elif size > max_size:
            mb = max_size // (1024 * 1024)
            result.issues.append(
                ValidationIssue(path, "error", f"File exceeds {mb}MB limit for category '{category}'")
            )
    return result
