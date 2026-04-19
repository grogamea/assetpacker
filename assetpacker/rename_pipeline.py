"""Integrate asset renaming into the build pipeline and apply renames on disk."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import shutil

from assetpacker.asset_renamer import RenameRule, RenameResult, rename_assets, build_rename_map


@dataclass
class RenamePipelineResult:
    results: List[RenameResult]
    errors: List[str] = field(default_factory=list)

    @property
    def rename_map(self) -> Dict[str, str]:
        return build_rename_map(self.results)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def run_rename_pipeline(
    src_paths: List[Path],
    output_dir: Path,
    rule: RenameRule,
    copy: bool = True,
) -> RenamePipelineResult:
    """Rename assets and optionally copy them to output_dir."""
    results = rename_assets(src_paths, rule)
    errors: List[str] = []

    if copy:
        output_dir.mkdir(parents=True, exist_ok=True)
        for r in results:
            dest = output_dir / r.renamed.name
            try:
                shutil.copy2(r.original, dest)
            except Exception as exc:
                errors.append(f"Failed to copy {r.original}: {exc}")

    return RenamePipelineResult(results=results, errors=errors)
