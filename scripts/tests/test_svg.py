"""Tests for core.svg — shared SVG builder functions."""

from core.svg import THEME, background_rect, escape, svg_header, title_bar


class TestEscape:
    def test_escapes_ampersand(self):
        assert escape("a & b") == "a &amp; b"

    def test_escapes_lt_gt(self):
        assert escape("x < y > z") == "x &lt; y &gt; z"

    def test_plain_text(self):
        assert escape("hello") == "hello"

    def test_empty(self):
        assert escape("") == ""


class TestSvgHeader:
    def test_contains_svg_tag(self):
        h = svg_header(100, 50)
        assert "<svg" in h
        assert "</style>" in h

    def test_viewbox(self):
        h = svg_header(100, 50)
        assert 'viewBox="0 0 100 50"' in h

    def test_font_no_external_import(self):
        h = svg_header(100, 50)
        assert "fonts.googleapis.com" not in h
        assert "@import" not in h

    def test_extra_defs(self):
        h = svg_header(100, 50, extra_defs="  .test { fill: red; }")
        assert ".test" in h


class TestTitleBar:
    def test_traffic_lights(self):
        t = title_bar(100, "test")
        assert THEME.red in t
        assert THEME.yellow in t
        assert THEME.green in t

    def test_prompt_text(self):
        t = title_bar(100, "my command")
        assert "my command" in t

    def test_prompt_escaped(self):
        t = title_bar(100, "echo & test")
        assert "&amp;" in t


class TestBackgroundRect:
    def test_bg_color(self):
        r = background_rect(100, 50)
        assert THEME.bg in r

    def test_dimensions(self):
        r = background_rect(100, 50)
        assert 'width="100"' in r
        assert 'height="50"' in r

    def test_custom_rx(self):
        r = background_rect(100, 50, rx="12")
        assert 'rx="12"' in r
