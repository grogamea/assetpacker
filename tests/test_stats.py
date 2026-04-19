import pytest
from unittest.mock import MagicMock
from assetpacker.stats import CategoryStats, BuildStats, compute_stats


def make_opt_result(category, original, output):
    r = MagicMock()
    r.category = category
    r.original_size = original
    r.output_size = output
    return r


@pytest.fixture
def optimize_summary():
    s = MagicMock()
    s.results = [
        make_opt_result("image", 2000, 1200),
        make_opt_result("image", 3000, 1800),
        make_opt_result("audio", 5000, 4000),
    ]
    s.total_original = 10000
    s.total_output = 7000
    return s


@pytest.fixture
def pack_result():
    p = MagicMock()
    p.bundle_size_kb = 6.84
    return p


def test_category_stats_savings(optimize_summary, pack_result):
    stats = compute_stats(optimize_summary, pack_result)
    image_cat = next(c for c in stats.category_stats if c.category == "image")
    assert image_cat.file_count == 2
    assert image_cat.original_bytes == 5000
    assert image_cat.optimized_bytes == 3000
    assert image_cat.savings_bytes == 2000
    assert image_cat.savings_pct == 40.0


def test_compute_stats_totals(optimize_summary, pack_result):
    stats = compute_stats(optimize_summary, pack_result)
    assert stats.total_files == 3
    assert stats.total_original_bytes == 10000
    assert stats.total_optimized_bytes == 7000
    assert stats.total_savings_bytes == 3000
    assert stats.total_savings_pct == 30.0


def test_compute_stats_bundle_size(optimize_summary, pack_result):
    stats = compute_stats(optimize_summary, pack_result)
    assert stats.bundle_size_kb == 6.84


def test_compute_stats_categories(optimize_summary, pack_result):
    stats = compute_stats(optimize_summary, pack_result)
    cats = {c.category for c in stats.category_stats}
    assert cats == {"image", "audio"}


def test_to_dict_keys(optimize_summary, pack_result):
    stats = compute_stats(optimize_summary, pack_result)
    d = stats.to_dict()
    assert "total_files" in d
    assert "total_savings_pct" in d
    assert "categories" in d
    assert isinstance(d["categories"], list)


def test_zero_original_savings_pct():
    cat = CategoryStats("font", 0, 0, 0)
    assert cat.savings_pct == 0.0


def test_build_stats_zero_original():
    stats = BuildStats(total_original_bytes=0, total_optimized_bytes=0)
    assert stats.total_savings_pct == 0.0
