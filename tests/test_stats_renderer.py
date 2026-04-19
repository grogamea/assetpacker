import pytest
from assetpacker.stats import BuildStats, CategoryStats
from assetpacker.stats_renderer import render_text, render_compact, render_markdown


@pytest.fixture
def stats():
    return BuildStats(
        category_stats=[
            CategoryStats("image", 2, 5000, 3000),
            CategoryStats("audio", 1, 5000, 4000),
        ],
        total_files=3,
        total_original_bytes=10000,
        total_optimized_bytes=7000,
        bundle_size_kb=6.84,
    )


def test_render_text_contains_totals(stats):
    out = render_text(stats)
    assert "3" in out
    assert "10,000" in out
    assert "7,000" in out
    assert "30.0%" in out


def test_render_text_contains_categories(stats):
    out = render_text(stats)
    assert "image" in out
    assert "audio" in out


def test_render_text_contains_bundle_size(stats):
    out = render_text(stats)
    assert "6.84" in out


def test_render_compact_single_line(stats):
    out = render_compact(stats)
    assert "\n" not in out
    assert "3 files" in out
    assert "6.84 KB" in out


def test_render_markdown_has_header(stats):
    out = render_markdown(stats)
    assert out.startswith("## Build Stats")


def test_render_markdown_has_table(stats):
    out = render_markdown(stats)
    assert "|" in out
    assert "image" in out
    assert "audio" in out


def test_render_markdown_savings(stats):
    out = render_markdown(stats)
    assert "30.0%" in out
