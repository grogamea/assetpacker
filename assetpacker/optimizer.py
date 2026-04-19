"""Asset optimization utilities for assetpacker."""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from assetpacker.config import PackerConfig
from assetpacker.scanner import AssetManifest


@dataclass
class OptimizeResult:
    source: Path
    dest: Path
    original_size: int
    optimized_size: int
    skipped: bool = False
    error: Optional[str] = None

    @property
    def savings_bytes(self) -> int:
        return self.original_size - self.optimized_size

    @property
    def savings_pct(self) -> float:
        if self.original_size == 0:
            return 0.0
        return (self.savings_bytes / self.original_size) * 100


@dataclass
class OptimizeSummary:
    results: List[OptimizeResult] = field(default_factory=list)

    @property
    def total_original(self) -> int:
        return sum(r.original_size for r in self.results)

    @property
    def total_optimized(self) -> int:
        return sum(r.optimized_size for r in self.results)

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if r.skipped)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.error)


def _copy_asset(src: Path, dest: Path) -> OptimizeResult:
    """Copy an asset to the output directory (stub for real optimization)."""
    original_size = src.stat().st_size
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    optimized_size = dest.stat().st_size
    return OptimizeResult(
        source=src,
        dest=dest,
        original_size=original_size,
        optimized_size=optimized_size,
    )


def optimize(manifest: AssetManifest, config: PackerConfig, output_dir: Path) -> OptimizeSummary:
    """Process all assets from manifest into output_dir according to config."""
    summary = OptimizeSummary()
    all_files = manifest.all_assets()

    for asset in all_files:
        rel = asset.relative_to(config.input_dir)
        dest = output_dir / rel
        try:
            result = _copy_asset(asset, dest)
        except Exception as exc:
            result = OptimizeResult(
                source=asset,
                dest=dest,
                original_size=asset.stat().st_size if asset.exists() else 0,
                optimized_size=0,
                error=str(exc),
            )
        summary.results.append(result)

    return summary
