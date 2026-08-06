#!/usr/bin/env python3
"""Tests for the fused profile header generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.github import _fallback_profile
from generators.header import build_header, render


def _make_profile(**overrides) -> dict:
    base = {
        "name": "Mahesh Diwan",
        "login": "mahesh-diwan",
        "commits": 1284,
        "merged_prs": 96,
        "reviews": 12,
        "closed_issues": 30,
        "repos": 15,
        "stars": 50,
        "followers": 150,
        "current_streak": 14,
        "longest_streak": 40,
        "languages": [
            {"name": "Python", "bytes": 5000},
            {"name": "Bash", "bytes": 3000},
            {"name": "Go", "bytes": 2000},
        ],
        "primary_language": "Python",
        "years": 3.0,
    }
    base.update(overrides)
    return base


class TestBuildHeader:
    def test_returns_svg(self):
        svg = build_header(_make_profile())
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")

    def test_contains_name_and_class(self):
        svg = build_header(_make_profile())
        assert "Mahesh Diwan" in svg
        assert "Automancer" in svg

    def test_contains_stat_chips(self):
        svg = build_header(_make_profile())
        assert "LVL" in svg
        assert "COMMITS" in svg
        assert "STREAK" in svg
        assert "1,284" in svg

    def test_smil_only_no_css_no_import(self):
        svg = build_header(_make_profile())
        assert "@keyframes" not in svg
        assert "@import" not in svg
        assert "fonts.googleapis.com" not in svg
        assert "<animate" in svg

    def test_earned_and_locked_pills(self):
        svg = build_header(_make_profile())
        assert 'fill="#00D4FF" opacity="0.15"' in svg  # earned pill (cyan fill)
        assert 'stroke="#8b949e" stroke-dasharray="4 3"' in svg  # locked pill (dashed)

    def test_name_escaped(self):
        svg = build_header(_make_profile(name="A & B"))
        assert "A &amp; B" in svg

    def test_fallback_profile_renders(self):
        """A zeroed profile (what render() gets when GraphQL fails) must not crash."""
        svg = build_header(_fallback_profile())
        assert svg.startswith("<svg")
        assert "LVL" in svg


class TestRender:
    def test_writes_file(self, tmp_path):
        out = tmp_path / "profile-header.svg"
        render(str(out), profile=_make_profile())
        assert out.read_text().startswith("<svg")
