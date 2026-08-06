#!/usr/bin/env python3
"""Tests for achievement rules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.achievements import ACHIEVEMENTS, compute_achievements


def _make_profile(**overrides) -> dict:
    base = {
        "name": "Test User",
        "login": "testuser",
        "commits": 0,
        "merged_prs": 0,
        "reviews": 0,
        "closed_issues": 0,
        "repos": 0,
        "stars": 0,
        "followers": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "languages": [],
        "primary_language": "Unknown",
        "years": 0,
    }
    base.update(overrides)
    return base


def _earned_ids(profile: dict) -> set[str]:
    return {a["id"] for a in compute_achievements(profile) if a["earned"]}


class TestAchievementRules:
    def test_all_earned_when_thresholds_met(self):
        profile = _make_profile(
            merged_prs=50,
            longest_streak=30,
            current_streak=14,
            stars=100,
            repos=5,
            languages=[{"name": "HCL", "bytes": 1}, {"name": "Go", "bytes": 1}],
            years=2,
        )
        assert _earned_ids(profile) == {
            "ship_it",
            "streak_lord",
            "night_owl",
            "star_surfer",
            "builder",
            "cloud_arch",
            "veteran",
        }

    def test_none_earned_on_zero_profile(self):
        assert _earned_ids(_make_profile()) == set()

    def test_empty_profile_no_crash(self):
        assert _earned_ids({}) == set()

    def test_boundary_ship_it(self):
        assert "ship_it" in _earned_ids(_make_profile(merged_prs=50))
        assert "ship_it" not in _earned_ids(_make_profile(merged_prs=49))

    def test_boundary_streak_lord(self):
        assert "streak_lord" in _earned_ids(_make_profile(longest_streak=30))
        assert "streak_lord" not in _earned_ids(_make_profile(longest_streak=29))

    def test_boundary_night_owl(self):
        assert "night_owl" in _earned_ids(_make_profile(current_streak=14))
        assert "night_owl" not in _earned_ids(_make_profile(current_streak=13))

    def test_boundary_star_surfer(self):
        assert "star_surfer" in _earned_ids(_make_profile(stars=100))
        assert "star_surfer" not in _earned_ids(_make_profile(stars=99))

    def test_boundary_builder(self):
        assert "builder" in _earned_ids(_make_profile(repos=5))
        assert "builder" not in _earned_ids(_make_profile(repos=4))

    def test_boundary_veteran(self):
        assert "veteran" in _earned_ids(_make_profile(years=2))
        assert "veteran" not in _earned_ids(_make_profile(years=1.9))

    def test_cloud_arch_needs_two_cloud_langs(self):
        two = _make_profile(
            languages=[{"name": "HCL", "bytes": 1}, {"name": "YAML", "bytes": 1}]
        )
        one = _make_profile(languages=[{"name": "HCL", "bytes": 1}])
        none = _make_profile(languages=[{"name": "Python", "bytes": 1}])
        assert "cloud_arch" in _earned_ids(two)
        assert "cloud_arch" not in _earned_ids(one)
        assert "cloud_arch" not in _earned_ids(none)


class TestAchievementShape:
    def test_has_expected_fields(self):
        for a in compute_achievements(_make_profile()):
            assert set(a.keys()) == {"id", "emoji", "name", "earned"}
            assert isinstance(a["earned"], bool)

    def test_order_matches_constant(self):
        computed = compute_achievements(_make_profile())
        assert [c["id"] for c in computed] == [a["id"] for a in ACHIEVEMENTS]
        assert len(computed) == 7
