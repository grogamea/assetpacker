"""Tests for assetpacker.watcher module."""

import time
from pathlib import Path

import pytest

from assetpacker.watcher import (
    WatchEvent,
    diff_snapshots,
    snapshot_directory,
    watch,
)


@pytest.fixture
def asset_tree(tmp_path):
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "hero.png").write_bytes(b"PNG")
    (tmp_path / "audio" / ).mkdir()
    (tmp_path / "audio" / "bgm.ogg").write_bytes(b"OGG")
    return tmp_path


def test_snapshot_returns_all_files(asset_tree):
    snap = snapshot_directory(asset_tree)
    paths = {Path(p).name for p in snap}
    assert "hero.png" in paths
    assert "bgm.ogg" in paths


def test_snapshot_stores_mtime(asset_tree):
    snap = snapshot_directory(asset_tree)
    for mtime in snap.values():
        assert isinstance(mtime, float)
        assert mtime > 0


def test_diff_detects_created():
    old = {"a.png": 1.0}
    new = {"a.png": 1.0, "b.png": 2.0}
    events = diff_snapshots(old, new)
    assert any(e.kind == "created" and e.path.name == "b.png" for e in events)


def test_diff_detects_modified():
    old = {"a.png": 1.0}
    new = {"a.png": 9.0}
    events = diff_snapshots(old, new)
    assert any(e.kind == "modified" and e.path.name == "a.png" for e in events)


def test_diff_detects_deleted():
    old = {"a.png": 1.0, "b.png": 2.0}
    new = {"b.png": 2.0}
    events = diff_snapshots(old, new)
    assert any(e.kind == "deleted" and e.path.name == "a.png" for e in events)


def test_diff_no_changes():
    snap = {"a.png": 1.0, "b.ogg": 2.0}
    assert diff_snapshots(snap, snap.copy()) == []


def test_watch_triggers_callback(tmp_path):
    (tmp_path / "file.txt").write_text("hello")
    collected: list = []

    def cb(events):
        collected.extend(events)

    # Run one cycle then modify a file
    import threading

    def modify():
        time.sleep(0.05)
        (tmp_path / "file.txt").write_text("changed")

    t = threading.Thread(target=modify)
    t.start()
    watch(tmp_path, cb, interval=0.02, max_cycles=5)
    t.join()
    assert any(e.kind == "modified" for e in collected)


def test_watch_event_str():
    e = WatchEvent(Path("img/hero.png"), "created", timestamp=1000.0)
    assert "created" in str(e)
    assert "hero.png" in str(e)
