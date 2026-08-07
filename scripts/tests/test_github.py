"""Tests for core.github — contribution fetching logic."""

from datetime import datetime, timezone

from core.github import _compute_stats, _deduplicate_days, _parse_profile


def _sample_user() -> dict:
    """Minimal GraphQL user payload matching PROFILE_QUERY shape."""
    day = {"date": "2026-08-05", "contributionCount": 3}
    return {
        "name": "Mahesh Diwan",
        "login": "mahesh-diwan",
        "createdAt": "2021-06-01T00:00:00Z",
        "contributionsCollection": {
            "totalCommitContributions": 100,
            "restrictedContributionsCount": 5,
            "totalPullRequestReviewContributions": 2,
            "contributionCalendar": {
                "weeks": [{"contributionDays": [day]}],
            },
        },
        "mergedPRs": {"totalCount": 10},
        "closedIssues": {"totalCount": 4},
        "season": {"totalContributions": 3},
        "repositories": {
            "totalCount": 6,
            "nodes": [
                {
                    "stargazers": {"totalCount": 50},
                    "languages": {"edges": [{"node": {"name": "Python"}, "size": 900}]},
                }
            ],
        },
        "followers": {"totalCount": 12},
    }


def test_parse_profile_does_not_raise_nameerror():
    profile = _parse_profile(_sample_user())
    assert profile["commits"] == 105
    assert profile["years"] > 0
    assert profile["languages"] == [{"name": "Python", "bytes": 900}]
    assert profile["current_streak"] == 1


def test_parse_profile_missing_stargazers():
    user = _sample_user()
    for repo in user["repositories"]["nodes"]:
        repo.pop("stargazers")
    profile = _parse_profile(user)
    assert profile["stars"] == 0
    assert profile["commits"] == 105
    assert profile["current_streak"] == 1


def test_parse_profile_empty_calendar():
    user = _sample_user()
    user["contributionsCollection"]["contributionCalendar"]["weeks"] = []
    profile = _parse_profile(user)
    assert profile["current_streak"] == 0
    assert profile["longest_streak"] == 0
    assert isinstance(profile["years"], float)


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
