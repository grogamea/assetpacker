"""Build report generation for assetpacker."""
from dataclasses import dataclass, field
from typing import List, Optional
import json
import datetime

from assetpacker.optimizer import OptimizeSummary
from assetpacker.packer import PackResult


@dataclass
class BuildReport:
    timestamp: str
    target: str
    optimize_summary: OptimizeSummary
    pack_result: PackResult
    warnings: List[str] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return self.pack_result.files_packed

    @property
    def output_path(self) -> str:
        return str(self.pack_result.output_path)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "target": self.target,
            "total_files": self.total_files,
            "original_size_kb": round(self.optimize_summary.total_original / 1024, 2),
            "optimized_size_kb": round(self.optimize_summary.total_optimized / 1024, 2),
            "savings_pct": round(self.optimize_summary.overall_savings_pct, 2),
            "output_path": self.output_path,
            "warnings": self.warnings,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_text(self) -> str:
        d = self.to_dict()
        lines = [
            f"=== AssetPacker Build Report ===",
            f"Timestamp : {d['timestamp']}",
            f"Target    : {d['target']}",
            f"Files     : {d['total_files']}",
            f"Original  : {d['original_size_kb']} KB",
            f"Optimized : {d['optimized_size_kb']} KB  (saved {d['savings_pct']}%)",
            f"Output    : {d['output_path']}",
        ]
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)


def generate_report(
    target: str,
    optimize_summary: OptimizeSummary,
    pack_result: PackResult,
    warnings: Optional[List[str]] = None,
) -> BuildReport:
    return BuildReport(
        timestamp=datetime.datetime.utcnow().isoformat() + "Z",
        target=target,
        optimize_summary=optimize_summary,
        pack_result=pack_result,
        warnings=warnings or [],
    )


def save_report(report: BuildReport, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(report.to_json())
