#!/usr/bin/env python3
"""Tests for svg_builder.py — pure functions for shared SVG markup."""

import pytest
from svg_builder import THEME, background_rect, escape, svg_header, title_bar


class TestEscape:
    def test_escapes_ampersand(self):
        assert escape("a & b") == "a &amp; b"

    def test_escapes_lt_gt(self):
        assert escape("x < y > z") == "x &lt; y &gt; z"

    def test_no_escape_for_plain_text(self):
        assert escape("hello world") == "hello world"

    def test_empty_string(self):
        assert escape("") == ""


class TestSvgHeader:
    def test_contains_svg_tag(self):
        h = svg_header(100, 50)
        assert "<svg" in h
        assert "</defs>" in h

    def test_contains_viewbox(self):
        h = svg_header(100, 50)
        assert 'viewBox="0 0 100 50"' in h

    def test_contains_font_import(self):
        h = svg_header(100, 50)
        assert "fonts.googleapis.com" in h

    def test_extra_defs_injected(self):
        h = svg_header(100, 50, extra_defs="  .test { fill: red; }")
        assert ".test" in h

    def test_no_extra_defs_when_empty(self):
        h = svg_header(100, 50)
        # Should still have the closing </defs>
        assert "</defs>" in h


class TestTitleBar:
    def test_contains_traffic_lights(self):
        t = title_bar(100, "test prompt")
        assert "#ff5f56" in t  # red
        assert "#ffbd2e" in t  # yellow
        assert "#27c93f" in t  # green

    def test_contains_prompt_text(self):
        t = title_bar(100, "my command")
        assert "my command" in t

    def test_prompt_escaped(self):
        t = title_bar(100, "echo & test")
        assert "&amp;" in t


class TestBackgroundRect:
    def test_contains_bg_color(self):
        r = background_rect(100, 50)
        assert "#0d1117" in r

    def test_contains_dimensions(self):
        r = background_rect(100, 50)
        assert 'width="100"' in r
        assert 'height="50"' in r

    def test_custom_rx(self):
        r = background_rect(100, 50, rx="12")
        assert 'rx="12"' in r


class TestTheme:
    def test_theme_has_required_keys(self):
        for key in ["BG", "FG", "ACCENT", "GREEN", "YELLOW"]:
            assert key in THEME

    def test_theme_accent_matches_cyan(self):
        assert THEME["ACCENT"] == "#00D4FF"

    def test_theme_bg_matches_expected(self):
        assert THEME["BG"] == "#0d1117"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
