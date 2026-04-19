"""Rename assets based on configurable patterns (e.g., content hash, prefix)."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from assetpacker.asset_hasher import hash_file


@dataclass
class RenameRule:
    pattern: str  # 'hash', 'prefix', 'flatten'
    prefix: str = ""
    hash_length: int = 8


@dataclass
class RenameResult:
    original: Path
    renamed: Path

    @property
    def changed(self) -> bool:
        return self.original != self.renamed


def _apply_rule(path: Path, rule: RenameRule) -> Path:
    if rule.pattern == "hash":
        result = hash_file(path)
        stem = path.stem + "." + result.short(rule.hash_length)
        return path.with_name(stem + path.suffix)
    elif rule.pattern == "prefix":
        return path.with_name(rule.prefix + path.name)
    elif rule.pattern == "flatten":
        return Path(path.name)
    return path


def rename_assets(paths: List[Path], rule: RenameRule) -> List[RenameResult]:
    results = []
    for p in paths:
        try:
            renamed = _apply_rule(p, rule)
        except Exception:
            renamed = p
        results.append(RenameResult(original=p, renamed=renamed))
    return results


def build_rename_map(results: List[RenameResult]) -> Dict[str, str]:
    return {str(r.original): str(r.renamed) for r in results if r.changed}


def describe_rename(results: List[RenameResult]) -> str:
    changed = [r for r in results if r.changed]
    lines = [f"Renamed {len(changed)}/{len(results)} assets:"]
    for r in changed:
        lines.append(f"  {r.original.name} -> {r.renamed.name}")
    return "\n".join(lines)
