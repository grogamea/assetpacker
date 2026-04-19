"""Packs optimized assets into a single output bundle (zip or folder)."""

import os
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from assetpacker.config import PackerConfig
from assetpacker.optimizer import OptimizeSummary


@dataclass
class PackResult:
    output_path: str
    files_packed: int
    bundle_size_bytes: int
    errors: List[str] = field(default_factory=list)

    @property
    def bundle_size_kb(self) -> float:
        return self.bundle_size_bytes / 1024

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def pack_to_zip(summary: OptimizeSummary, config: PackerConfig) -> PackResult:
    output_path = os.path.join(config.output_dir, "assets.zip")
    os.makedirs(config.output_dir, exist_ok=True)
    errors = []
    files_packed = 0

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for result in summary.results:
            src = result.output_path
            if not os.path.isfile(src):
                errors.append(f"Missing file: {src}")
                continue
            arcname = os.path.relpath(src, config.output_dir)
            zf.write(src, arcname)
            files_packed += 1

    bundle_size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
    return PackResult(output_path=output_path, files_packed=files_packed,
                      bundle_size_bytes=bundle_size, errors=errors)


def pack_to_folder(summary: OptimizeSummary, config: PackerConfig) -> PackResult:
    output_path = os.path.join(config.output_dir, "bundle")
    os.makedirs(output_path, exist_ok=True)
    errors = []
    files_packed = 0
    total_size = 0

    for result in summary.results:
        src = result.output_path
        if not os.path.isfile(src):
            errors.append(f"Missing file: {src}")
            continue
        dest = os.path.join(output_path, os.path.basename(src))
        shutil.copy2(src, dest)
        total_size += os.path.getsize(dest)
        files_packed += 1

    return PackResult(output_path=output_path, files_packed=files_packed,
                      bundle_size_bytes=total_size, errors=errors)


def pack(summary: OptimizeSummary, config: PackerConfig) -> PackResult:
    if getattr(config, "bundle_format", "zip") == "folder":
        return pack_to_folder(summary, config)
    return pack_to_zip(summary, config)
