#!/usr/bin/env python3
"""Tests for the contribution heatmap generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.heatmap import render


def _make_data(**overrides) -> dict:
    data = {
        "total_contributions": 68,
        "days": [
            {"date": "2025-08-03", "level": 0},
            {"date": "2025-08-04", "level": 2},
            {"date": "2025-08-05", "level": 5},
            {"date": "2025-08-06", "level": 1},
        ],
    }
    data.update(overrides)
    return data


class TestRender:
    def test_renders_full_svg(self, tmp_path):
        out = tmp_path / "contrib-heatmap.svg"
        render(_make_data(), str(out))
        content = out.read_text()
        assert content.startswith("<svg")
        assert content.endswith("</svg>")
        assert "<svg" in content

    def test_renders_without_days(self, tmp_path):
        out = tmp_path / "contrib-heatmap.svg"
        render(_make_data(days=[]), str(out))
        assert out.read_text().startswith("<svg")

    def test_skips_malformed_dates(self, tmp_path):
        out = tmp_path / "contrib-heatmap.svg"
        data = _make_data(
            days=[
                {"date": "not-a-date", "level": 2},
                {"date": "2025-08-05", "level": 3},
            ]
        )
        render(data, str(out))
        assert "<svg" in out.read_text()

    def test_uses_theme_surface_and_muted(self, tmp_path):
        out = tmp_path / "contrib-heatmap.svg"
        render(_make_data(), str(out))
        content = out.read_text()
        assert "#161b22" in content
        assert "#8b949e" in content
