"""Utilities for hashing asset files for cache invalidation and deduplication."""

import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List


BUFFER_SIZE = 65536


@dataclass
class HashResult:
    path: Path
    hex: str
    size_bytes: int

    def short(self, length: int = 8) -> str:
        return self.hex[:length]


def hash_file(path: Path, algorithm: str = "sha256") -> HashResult:
    """Compute a hash of a single file."""
    h = hashlib.new(algorithm)
    size = 0
    with open(path, "rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            h.update(chunk)
            size += len(chunk)
    return HashResult(path=path, hex=h.hexdigest(), size_bytes=size)


def hash_files(paths: List[Path], algorithm: str = "sha256") -> Dict[Path, HashResult]:
    """Hash multiple files and return a mapping from path to HashResult."""
    return {p: hash_file(p, algorithm) for p in paths}


def find_duplicates(results: Dict[Path, HashResult]) -> Dict[str, List[Path]]:
    """Group paths by hash to identify duplicate file contents."""
    groups: Dict[str, List[Path]] = {}
    for path, result in results.items():
        groups.setdefault(result.hex, []).append(path)
    return {h: paths for h, paths in groups.items() if len(paths) > 1}


def describe_duplicates(dupes: Dict[str, List[Path]]) -> str:
    if not dupes:
        return "No duplicate assets found."
    lines = [f"{len(dupes)} duplicate group(s) detected:"]
    for h, paths in dupes.items():
        lines.append(f"  [{h[:8]}] {len(paths)} files")
        for p in paths:
            lines.append(f"    - {p}")
    return "\n".join(lines)
