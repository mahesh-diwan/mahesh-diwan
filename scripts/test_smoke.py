#!/usr/bin/env python3
"""Smoke tests: verify all scripts import and core functions exist."""

import ast
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)


def test_syntax():
    """Every .py file in scripts/ must parse without syntax errors."""
    for fname in os.listdir(SCRIPTS_DIR):
        if not fname.endswith(".py") or fname == "test_smoke.py":
            continue
        path = os.path.join(SCRIPTS_DIR, fname)
        with open(path) as f:
            ast.parse(f.read(), filename=fname)
        print(f"  syntax OK: {fname}")


def test_imports():
    """Core modules must import cleanly (skips runtime deps like bs4/rembg)."""
    # These only use stdlib + pillow/numpy which are always available
    sys.path.insert(0, REPO_ROOT)
    from scripts.make_ascii_svg import make_ascii, RAMP
    from scripts.make_info_card import render as info_render, escape, LINES
    from scripts.render_heatmap_svg import render as heatmap_render, PALETTE

    assert len(RAMP) > 0, "RAMP is empty"
    assert len(PALETTE) > 0, "PALETTE is empty"
    assert len(LINES) > 0, "LINES is empty"
    assert callable(make_ascii)
    assert callable(info_render)
    assert callable(heatmap_render)
    assert callable(escape)
    print("  imports OK: make_ascii_svg, make_info_card, render_heatmap_svg")


def test_escape():
    """escape() handles XML special chars."""
    from scripts.make_info_card import escape

    assert escape("a&b") == "a&amp;b"
    assert escape("<tag>") == "&lt;tag&gt;"
    assert escape("plain") == "plain"
    print("  escape() OK")


def test_ascii_ramp():
    """RAMP covers full luminance range."""
    from scripts.make_ascii_svg import RAMP

    assert RAMP[0] == " ", "darkest char should be space"
    assert len(RAMP) >= 10, "RAMP too short for meaningful ASCII art"
    print(f"  RAMP OK: {len(RAMP)} chars")


if __name__ == "__main__":
    print("Running smoke tests...")
    test_syntax()
    test_imports()
    test_escape()
    test_ascii_ramp()
    print("All smoke tests passed.")
