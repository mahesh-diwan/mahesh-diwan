"""Tests for core.theme — design tokens."""

from core.theme import THEME, Theme


def test_theme_is_frozen():
    assert isinstance(THEME, Theme)
    try:
        THEME.bg = "#fff"
        assert False, "Should be frozen"
    except AttributeError:
        pass


def test_theme_colors_are_hex():
    for attr in ("bg", "surface", "fg", "muted", "cyan", "green", "yellow", "red"):
        val = getattr(THEME, attr)
        assert val.startswith("#"), f"{attr} should start with #"
        assert len(val) == 7, f"{attr} should be 7 chars"


def test_font_css_contains_import():
    assert "fonts.googleapis.com" in THEME.font_css
    assert "Fragment Mono" in THEME.font_css
