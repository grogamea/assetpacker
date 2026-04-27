"""Asset scoring module — ranks assets by priority for packing order and optimization."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from assetpacker.scanner import AssetManifest


# Weight table: higher score = higher priority
_CATEGORY_WEIGHTS: Dict[str, float] = {
    "fonts": 1.0,
    "images": 0.8,
    "audio": 0.6,
    "video": 0.4,
    "data": 0.3,
    "other": 0.1,
}

_SIZE_PENALTY_THRESHOLD_KB = 500
_SIZE_PENALTY_FACTOR = 0.0001


@dataclass
class AssetScore:
    path: Path
    category: str
    size_bytes: int
    score: float

    @property
    def size_kb(self) -> float:
        return self.size_bytes / 1024

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "category": self.category,
            "size_bytes": self.size_bytes,
            "size_kb": round(self.size_kb, 2),
            "score": round(self.score, 4),
        }


@dataclass
class ScoredManifest:
    entries: List[AssetScore] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    def top(self, n: int = 10) -> List[AssetScore]:
        return self.entries[:n]

    def by_category(self, category: str) -> List[AssetScore]:
        return [e for e in self.entries if e.category == category]


def _compute_score(category: str, size_bytes: int) -> float:
    base = _CATEGORY_WEIGHTS.get(category, 0.1)
    size_kb = size_bytes / 1024
    penalty = max(0.0, (size_kb - _SIZE_PENALTY_THRESHOLD_KB) * _SIZE_PENALTY_FACTOR)
    return max(0.0, base - penalty)


def score_assets(manifest: AssetManifest) -> ScoredManifest:
    """Score and rank all assets in the manifest by priority."""
    scored: List[AssetScore] = []

    for category, paths in [
        ("fonts", manifest.fonts),
        ("images", manifest.images),
        ("audio", manifest.audio),
        ("other", manifest.other),
    ]:
        for path in paths:
            size = path.stat().st_size if path.exists() else 0
            s = _compute_score(category, size)
            scored.append(AssetScore(path=path, category=category, size_bytes=size, score=s))

    scored.sort(key=lambda e: e.score, reverse=True)
    return ScoredManifest(entries=scored)


def describe_scores(sm: ScoredManifest, top_n: int = 5) -> str:
    lines = [f"Asset scores (top {top_n} of {sm.total}):"] + [
        f"  [{e.score:.3f}] {e.path.name} ({e.category}, {e.size_kb:.1f} KB)"
        for e in sm.top(top_n)
    ]
    return "\n".join(lines)
