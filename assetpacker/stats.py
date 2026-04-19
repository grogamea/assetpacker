from dataclasses import dataclass, field
from typing import Dict, List
from assetpacker.optimizer import OptimizeSummary
from assetpacker.packer import PackResult


@dataclass
class CategoryStats:
    category: str
    file_count: int
    original_bytes: int
    optimized_bytes: int

    @property
    def savings_bytes(self) -> int:
        return self.original_bytes - self.optimized_bytes

    @property
    def savings_pct(self) -> float:
        if self.original_bytes == 0:
            return 0.0
        return round(100.0 * self.savings_bytes / self.original_bytes, 2)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "file_count": self.file_count,
            "original_bytes": self.original_bytes,
            "optimized_bytes": self.optimized_bytes,
            "savings_bytes": self.savings_bytes,
            "savings_pct": self.savings_pct,
        }


@dataclass
class BuildStats:
    category_stats: List[CategoryStats] = field(default_factory=list)
    total_files: int = 0
    total_original_bytes: int = 0
    total_optimized_bytes: int = 0
    bundle_size_kb: float = 0.0

    @property
    def total_savings_bytes(self) -> int:
        return self.total_original_bytes - self.total_optimized_bytes

    @property
    def total_savings_pct(self) -> float:
        if self.total_original_bytes == 0:
            return 0.0
        return round(100.0 * self.total_savings_bytes / self.total_original_bytes, 2)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "total_original_bytes": self.total_original_bytes,
            "total_optimized_bytes": self.total_optimized_bytes,
            "total_savings_bytes": self.total_savings_bytes,
            "total_savings_pct": self.total_savings_pct,
            "bundle_size_kb": self.bundle_size_kb,
            "categories": [c.to_dict() for c in self.category_stats],
        }


def compute_stats(optimize_summary: OptimizeSummary, pack_result: PackResult) -> BuildStats:
    category_map: Dict[str, CategoryStats] = {}
    for result in optimize_summary.results:
        cat = result.category
        if cat not in category_map:
            category_map[cat] = CategoryStats(cat, 0, 0, 0)
        category_map[cat].file_count += 1
        category_map[cat].original_bytes += result.original_size
        category_map[cat].optimized_bytes += result.output_size

    return BuildStats(
        category_stats=list(category_map.values()),
        total_files=len(optimize_summary.results),
        total_original_bytes=optimize_summary.total_original,
        total_optimized_bytes=optimize_summary.total_output,
        bundle_size_kb=pack_result.bundle_size_kb,
    )
