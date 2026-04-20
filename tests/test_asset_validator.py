import pytest
from pathlib import Path
from assetpacker.asset_validator import validate_assets, ValidationIssue


@pytest.fixture
def asset_tree(tmp_path):
    img = tmp_path / "sprite.png"
    img.write_bytes(b"\x89PNG" + b"x" * 100)
    audio = tmp_path / "music.mp3"
    audio.write_bytes(b"x" * 200)
    empty = tmp_path / "empty.png"
    empty.write_bytes(b"")
    return tmp_path, img, audio, empty


def test_valid_files_no_errors(asset_tree):
    _, img, audio, _ = asset_tree
    result = validate_assets([img, audio])
    assert result.valid
    assert len(result.errors) == 0


def test_empty_file_is_warning(asset_tree):
    _, _, _, empty = asset_tree
    result = validate_assets([empty])
    assert result.valid  # warning, not error
    assert len(result.warnings) == 1
    assert "empty" in result.warnings[0].message.lower()


def test_missing_file_is_error(tmp_path):
    missing = tmp_path / "ghost.png"
    result = validate_assets([missing])
    assert not result.valid
    assert any("does not exist" in i.message for i in result.errors)


def test_oversized_file_is_error(tmp_path):
    big = tmp_path / "huge.png"
    big.write_bytes(b"x" * (11 * 1024 * 1024))  # 11MB > 10MB image limit
    result = validate_assets([big])
    assert not result.valid
    assert any("exceeds" in i.message for i in result.errors)


def test_summary_format(asset_tree):
    _, _, _, empty = asset_tree
    result = validate_assets([empty])
    s = result.summary()
    assert "error" in s
    assert "warning" in s


def test_issue_str_format(tmp_path):
    p = tmp_path / "x.png"
    issue = ValidationIssue(p, "error", "something bad")
    assert "ERROR" in str(issue)
    assert "something bad" in str(issue)


def test_multiple_files_mixed(asset_tree, tmp_path):
    _, img, _, empty = asset_tree
    missing = tmp_path / "no.png"
    result = validate_assets([img, empty, missing])
    assert not result.valid
    assert len(result.errors) == 1
    assert len(result.warnings) == 1
