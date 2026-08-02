#!/usr/bin/env python3
"""Tests for fetch_contributions.py pure logic: dedup, stats, monthly."""

from scripts.fetch_contributions import deduplicate_days, compute_stats


def test_deduplicate_keeps_max_level():
    days = [
        {"date": "2025-01-03", "level": 1},
        {"date": "2025-01-01", "level": 2},
        {"date": "2025-01-02", "level": 0},
        {"date": "2025-01-01", "level": 5},
    ]
    result = deduplicate_days(days)
    assert len(result) == 3
    assert result[0]["date"] == "2025-01-01"
    assert result[0]["level"] == 5


def test_deduplicate_empty():
    assert deduplicate_days([]) == []


def test_compute_stats_total():
    days = [
        {"date": "2025-01-01", "level": 3},
        {"date": "2025-01-02", "level": 2},
        {"date": "2025-01-03", "level": 0},
    ]
    stats = compute_stats(days)
    assert stats["total"] == 5
    assert stats["longest_streak"] == 2
    assert stats["current_streak"] == 0  # last day is level 0


def test_compute_stats_best_day():
    days = [
        {"date": "2025-01-01", "level": 1},
        {"date": "2025-01-02", "level": 4},
        {"date": "2025-01-03", "level": 2},
    ]
    stats = compute_stats(days)
    assert stats["best_day"]["level"] == 4
    assert stats["best_day"]["date"] == "2025-01-02"


def test_compute_stats_monthly():
    days = [
        {"date": "2025-01-01", "level": 3},
        {"date": "2025-01-15", "level": 2},
        {"date": "2025-02-01", "level": 1},
    ]
    stats = compute_stats(days)
    assert stats["monthly_totals"]["2025-01"] == 5
    assert stats["monthly_totals"]["2025-02"] == 1


def test_compute_stats_all_zero():
    days = [{"date": f"2025-01-{i:02d}", "level": 0} for i in range(1, 8)]
    stats = compute_stats(days)
    assert stats["total"] == 0
    assert stats["longest_streak"] == 0
    assert stats["current_streak"] == 0
    assert stats["best_day"] == {"date": None, "level": 0}


def test_compute_stats_empty():
    stats = compute_stats([])
    assert stats["total"] == 0
    assert stats["longest_streak"] == 0
    assert stats["current_streak"] == 0


if __name__ == "__main__":
    test_deduplicate_keeps_max_level()
    test_deduplicate_empty()
    test_compute_stats_total()
    test_compute_stats_best_day()
    test_compute_stats_monthly()
    test_compute_stats_all_zero()
    test_compute_stats_empty()
    print("All fetch_contributions tests passed.")
