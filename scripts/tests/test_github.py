"""Tests for core.github — contribution fetching logic."""

from core.github import _compute_stats, _deduplicate_days


def test_deduplicate_keeps_max_level():
    days = [
        {"date": "2025-01-03", "level": 1},
        {"date": "2025-01-01", "level": 2},
        {"date": "2025-01-02", "level": 0},
        {"date": "2025-01-01", "level": 5},
    ]
    result = _deduplicate_days(days)
    assert len(result) == 3
    assert result[0]["date"] == "2025-01-01"
    assert result[0]["level"] == 5


def test_deduplicate_empty():
    assert _deduplicate_days([]) == []


def test_compute_stats_total():
    days = [
        {"date": "2025-01-01", "level": 3},
        {"date": "2025-01-02", "level": 2},
        {"date": "2025-01-03", "level": 0},
    ]
    stats = _compute_stats(days)
    assert stats["total"] == 5
    assert stats["longest_streak"] == 2
    assert stats["current_streak"] == 0


def test_compute_stats_best_day():
    days = [
        {"date": "2025-01-01", "level": 1},
        {"date": "2025-01-02", "level": 4},
        {"date": "2025-01-03", "level": 2},
    ]
    stats = _compute_stats(days)
    assert stats["best_day"]["level"] == 4
    assert stats["best_day"]["date"] == "2025-01-02"


def test_compute_stats_monthly():
    days = [
        {"date": "2025-01-01", "level": 3},
        {"date": "2025-01-15", "level": 2},
        {"date": "2025-02-01", "level": 1},
    ]
    stats = _compute_stats(days)
    assert stats["monthly_totals"]["2025-01"] == 5
    assert stats["monthly_totals"]["2025-02"] == 1


def test_compute_stats_empty():
    stats = _compute_stats([])
    assert stats["total"] == 0
    assert stats["longest_streak"] == 0
    assert stats["current_streak"] == 0
