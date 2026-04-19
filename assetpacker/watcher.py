"""File system watcher for incremental rebuilds."""

from __future__ import annotations

import time
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional


@dataclass
class WatchEvent:
    path: Path
    kind: str  # 'modified' | 'created' | 'deleted'
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        return f"[{self.kind}] {self.path} at {self.timestamp:.2f}"


@dataclass
class WatcherState:
    snapshots: Dict[str, float] = field(default_factory=dict)

    def update(self, path: str, mtime: float) -> None:
        self.snapshots[path] = mtime

    def remove(self, path: str) -> None:
        self.snapshots.pop(path, None)


def snapshot_directory(root: Path) -> Dict[str, float]:
    """Return a mapping of file path -> mtime for all files under root."""
    result: Dict[str, float] = {}
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            full = Path(dirpath) / fname
            try:
                result[str(full)] = full.stat().st_mtime
            except OSError:
                pass
    return result


def diff_snapshots(
    old: Dict[str, float], new: Dict[str, float]
) -> list[WatchEvent]:
    """Compute WatchEvents between two directory snapshots."""
    events: list[WatchEvent] = []
    for path, mtime in new.items():
        if path not in old:
            events.append(WatchEvent(Path(path), "created"))
        elif old[path] != mtime:
            events.append(WatchEvent(Path(path), "modified"))
    for path in old:
        if path not in new:
            events.append(WatchEvent(Path(path), "deleted"))
    return events


def watch(
    root: Path,
    callback: Callable[[list[WatchEvent]], None],
    interval: float = 1.0,
    max_cycles: Optional[int] = None,
) -> None:
    """Poll root directory and invoke callback when changes are detected."""
    current = snapshot_directory(root)
    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        time.sleep(interval)
        updated = snapshot_directory(root)
        events = diff_snapshots(current, updated)
        if events:
            callback(events)
        current = updated
        cycles += 1
