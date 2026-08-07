#!/usr/bin/env python3
"""Tests for the section-header banner generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.banners import BANNERS, render

SLUGS = ["status", "arcade", "ssh", "activity", "projects", "blog", "agents"]


class TestBanners:
    def test_seven_slugs(self):
        assert list(BANNERS) == SLUGS

    def test_render_writes_all_files(self, tmp_path):
        render(str(tmp_path))
        for slug in SLUGS:
            assert (tmp_path / f"header-{slug}.svg").exists()

    def test_files_are_full_svg(self, tmp_path):
        render(str(tmp_path))
        for slug in SLUGS:
            content = (tmp_path / f"header-{slug}.svg").read_text()
            assert content.startswith("<svg")
            assert "<style>" in content
            assert content.endswith("</svg>")

    def test_terminal_banners_contain_prompt(self, tmp_path):
        render(str(tmp_path))
        for slug in ("arcade", "ssh"):
            content = (tmp_path / f"header-{slug}.svg").read_text()
            assert "mahesh@github ~ $" in content

    def test_status_contains_text(self, tmp_path):
        render(str(tmp_path))
        content = (tmp_path / "header-status.svg").read_text()
        assert "refactoring flexfetch" in content
