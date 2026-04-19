import pytest
from pathlib import Path
from assetpacker.asset_hasher import (
    hash_file, hash_files, find_duplicates, describe_duplicates, HashResult
)


@pytest.fixture
def asset_tree(tmp_path):
    (tmp_path / "a.png").write_bytes(b"imagedata")
    (tmp_path / "b.png").write_bytes(b"imagedata")  # duplicate of a.png
    (tmp_path / "c.ogg").write_bytes(b"audiodata")
    return tmp_path


def test_hash_file_returns_result(asset_tree):
    result = hash_file(asset_tree / "a.png")
    assert isinstance(result, HashResult)
    assert len(result.hex) == 64  # sha256
    assert result.size_bytes == len(b"imagedata")


def test_hash_file_short(asset_tree):
    result = hash_file(asset_tree / "a.png")
    assert result.short() == result.hex[:8]
    assert result.short(4) == result.hex[:4]


def test_identical_files_same_hash(asset_tree):
    r1 = hash_file(asset_tree / "a.png")
    r2 = hash_file(asset_tree / "b.png")
    assert r1.hex == r2.hex


def test_different_files_different_hash(asset_tree):
    r1 = hash_file(asset_tree / "a.png")
    r2 = hash_file(asset_tree / "c.ogg")
    assert r1.hex != r2.hex


def test_hash_files_returns_all(asset_tree):
    paths = [asset_tree / "a.png", asset_tree / "c.ogg"]
    results = hash_files(paths)
    assert set(results.keys()) == set(paths)


def test_find_duplicates_detects_dupes(asset_tree):
    paths = [asset_tree / "a.png", asset_tree / "b.png", asset_tree / "c.ogg"]
    results = hash_files(paths)
    dupes = find_duplicates(results)
    assert len(dupes) == 1
    group = next(iter(dupes.values()))
    assert len(group) == 2


def test_find_duplicates_no_dupes(asset_tree):
    paths = [asset_tree / "a.png", asset_tree / "c.ogg"]
    results = hash_files(paths)
    dupes = find_duplicates(results)
    assert dupes == {}


def test_describe_duplicates_no_dupes():
    assert describe_duplicates({}) == "No duplicate assets found."


def test_describe_duplicates_with_dupes(asset_tree):
    paths = [asset_tree / "a.png", asset_tree / "b.png"]
    results = hash_files(paths)
    dupes = find_duplicates(results)
    text = describe_duplicates(dupes)
    assert "1 duplicate group" in text
    assert "2 files" in text
