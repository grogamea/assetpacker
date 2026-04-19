"""Tests for manifest_writer module."""
import json
import csv
import pytest
from pathlib import Path

from assetpacker.scanner import AssetManifest
from assetpacker.manifest_writer import write_manifest


@pytest.fixture()
def manifest(tmp_path):
    base = tmp_path / "assets"
    (base / "img").mkdir(parents=True)
    (base / "snd").mkdir()
    img1 = base / "img" / "hero.png"
    img2 = base / "img" / "bg.jpg"
    snd1 = base / "snd" / "jump.wav"
    for f in (img1, img2, snd1):
        f.write_bytes(b"x")
    m = AssetManifest()
    m.images = [img1, img2]
    m.audio = [snd1]
    m.fonts = []
    m.data = []
    m.other = []
    return m


def test_write_json_creates_file(manifest, tmp_path):
    out = tmp_path / "out" / "manifest.json"
    result = write_manifest(manifest, out, fmt="json")
    assert result == out
    assert out.exists()


def test_write_json_structure(manifest, tmp_path):
    out = tmp_path / "manifest.json"
    write_manifest(manifest, out, fmt="json")
    data = json.loads(out.read_text())
    assert data["total"] == 3
    assert len(data["categories"]["images"]) == 2
    assert len(data["categories"]["audio"]) == 1


def test_write_csv_creates_file(manifest, tmp_path):
    out = tmp_path / "manifest.csv"
    write_manifest(manifest, out, fmt="csv")
    assert out.exists()


def test_write_csv_rows(manifest, tmp_path):
    out = tmp_path / "manifest.csv"
    write_manifest(manifest, out, fmt="csv")
    rows = list(csv.reader(out.read_text().splitlines()))
    assert rows[0] == ["category", "path"]
    categories = [r[0] for r in rows[1:]]
    assert categories.count("images") == 2
    assert categories.count("audio") == 1


def test_write_txt_creates_file(manifest, tmp_path):
    out = tmp_path / "manifest.txt"
    write_manifest(manifest, out, fmt="txt")
    assert out.exists()


def test_write_txt_contains_sections(manifest, tmp_path):
    out = tmp_path / "manifest.txt"
    write_manifest(manifest, out, fmt="txt")
    text = out.read_text()
    assert "[images]" in text
    assert "[audio]" in text
    assert "hero.png" in text


def test_write_unknown_format_raises(manifest, tmp_path):
    with pytest.raises(ValueError, match="Unknown format"):
        write_manifest(manifest, tmp_path / "x.bin", fmt="bin")  # type: ignore


def test_write_creates_parent_dirs(manifest, tmp_path):
    out = tmp_path / "deep" / "nested" / "manifest.json"
    write_manifest(manifest, out, fmt="json")
    assert out.exists()
