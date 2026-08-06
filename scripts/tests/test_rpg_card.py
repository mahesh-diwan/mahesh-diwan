#!/usr/bin/env python3
"""Tests for RPG card character computation."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.rpg_card import compute_character, _get_rarity, _get_class


def _make_profile(**overrides) -> dict:
    """Build a minimal profile dict with sensible defaults."""
    base = {
        "name": "Test User",
        "login": "testuser",
        "commits": 100,
        "merged_prs": 20,
        "reviews": 15,
        "closed_issues": 30,
        "repos": 10,
        "stars": 50,
        "followers": 25,
        "current_streak": 7,
        "longest_streak": 30,
        "languages": [{"name": "Python", "bytes": 10000}],
        "primary_language": "Python",
        "years": 2.0,
    }
    base.update(overrides)
    return base


class TestComputeCharacter:
    def test_basic_xp_computation(self):
        profile = _make_profile()
        char = compute_character(profile)
        assert char["level"] >= 0
        assert char["total_xp"] > 0
        assert 0 <= char["progress"] <= 1.0

    def test_level_formula(self):
        """Level = floor(sqrt(totalXP / 100))."""
        profile = _make_profile()
        char = compute_character(profile)
        expected_level = int(math.sqrt(char["total_xp"] / 100))
        assert char["level"] == expected_level

    def test_zero_activity(self):
        profile = _make_profile(
            commits=0,
            merged_prs=0,
            reviews=0,
            closed_issues=0,
            repos=0,
            stars=0,
            followers=0,
            current_streak=0,
            years=0,
        )
        char = compute_character(profile)
        assert char["level"] == 0
        assert char["total_xp"] == 0

    def test_high_activity_gives_higher_level(self):
        low = compute_character(_make_profile(commits=10))
        high = compute_character(_make_profile(commits=1000))
        assert high["level"] > low["level"]

    def test_streak_increases_xp(self):
        no_streak = compute_character(_make_profile(current_streak=0))
        with_streak = compute_character(_make_profile(current_streak=100))
        assert with_streak["total_xp"] > no_streak["total_xp"]

    def test_tenure_multiplier(self):
        short = compute_character(_make_profile(years=1))
        long = compute_character(_make_profile(years=10))
        assert long["total_xp"] > short["total_xp"]

    def test_class_mapping(self):
        profile = _make_profile(primary_language="Python")
        char = compute_character(profile)
        assert char["class_name"] == "Automancer"

        profile = _make_profile(primary_language="Go")
        char = compute_character(profile)
        assert char["class_name"] == "Gopher Knight"

    def test_unknown_language_uses_default(self):
        profile = _make_profile(primary_language="Zig")
        char = compute_character(profile)
        assert char["class_name"] == "DevOps Sentinel"

    def test_rarity_tiers(self):
        assert _get_rarity(0) == ("Common", "#8b949e")
        assert _get_rarity(10) == ("Rare", "#58a6ff")
        assert _get_rarity(25) == ("Epic", "#a371f7")
        assert _get_rarity(50) == ("Legendary", "#f0883e")
        assert _get_rarity(100) == ("Mythic", "#ff7b72")

    def test_class_mapping_all_keys(self):
        """Every class key in CLASSES maps to a valid class."""
        from generators.rpg_card import CLASSES

        for lang, (cls, desc) in CLASSES.items():
            assert isinstance(cls, str) and len(cls) > 0
            assert isinstance(desc, str) and len(desc) > 0

    def test_progress_capped_at_1(self):
        """Progress should never exceed 1.0."""
        profile = _make_profile(commits=5000, merged_prs=500, years=15)
        char = compute_character(profile)
        assert char["progress"] <= 1.0
