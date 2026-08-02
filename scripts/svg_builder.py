#!/usr/bin/env python3
"""
Shared SVG builder for profile art generators.

Extracts the duplicated SVG boilerplate (font imports, background, title bar)
from make_ascii_svg.py, make_info_card.py, and render_heatmap_svg.py.

Usage:

    from svg_builder import svg_header, title_bar, escape

    parts = [
        svg_header(width=W, height=H),
        title_bar(W, "mahesh@github ~ $ ./script.sh"),
        # ... content ...
        "</svg>",
    ]
"""

from xml.sax.saxutils import escape as _xml_escape

# Shared terminal theme palette
BG = "#0d1117"  # darkest — SVG background
SURFACE = "#161b22"  # secondary — title bar
TEXT_MUTED = "#8b949e"  # dim text
CYAN = "#00D4FF"  # accent
GREEN = "#27c93f"  # traffic light / neofetch green
YELLOW = "#ffbd2e"  # traffic light / neofetch yellow
RED = "#ff5f56"  # traffic light

# Convenience dict for modules that need the full palette (e.g. make_info_card)
THEME = {
    "BG": BG,
    "FG": "#c9d1d9",
    "SURFACE": SURFACE,
    "ACCENT": CYAN,
    "GREEN": GREEN,
    "YELLOW": YELLOW,
    "RED": RED,
    "TEXT_MUTED": TEXT_MUTED,
}

# Font CSS shared across all SVGs
FONT_CSS = (
    '    @import url("https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500'
    '&family=Fragment+Mono:wght@400;500;700&display=swap");'
    "\n    text {"
    ' font-family: "Fragment Mono", "DM Mono", "Fira Code",'
    " ui-monospace, SFMono-Regular, SF Mono, Menlo, Monaco, Consolas, monospace;"
    " }"
)


def escape(text):
    """Escape XML special characters for SVG text content."""
    return _xml_escape(str(text))


def svg_header(width, height, extra_defs=""):
    """Build the opening ``<svg>`` tag with shared font CSS in ``<defs>``.

    Args:
        width: SVG width in pixels.
        height: SVG height in pixels.
        extra_defs: Optional additional ``<defs>`` content to inject.

    Returns:
        String of opening SVG markup.
    """
    defs = f"    {FONT_CSS}\n"
    if extra_defs:
        defs += f"    {extra_defs}\n"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
        "  <defs>\n"
        f"{defs}"
        "  </defs>\n"
    )


def title_bar(width, prompt):
    """Build the macOS-style traffic-light title bar.

    Args:
        width: Total SVG width (for centering the prompt text).
        prompt: Terminal command string, e.g. ``mahesh@github ~ $ ./script.sh``.

    Returns:
        String of SVG markup for the title bar.
    """
    return (
        f'<rect x="0" y="0" width="{width}" height="32" fill="{SURFACE}" rx="8"/>\n'
        f'<circle cx="16" cy="16" r="6" fill="{RED}"/>\n'
        f'<circle cx="36" cy="16" r="6" fill="{YELLOW}"/>\n'
        f'<circle cx="56" cy="16" r="6" fill="{GREEN}"/>\n'
        f'<text x="{width // 2}" y="22" fill="{TEXT_MUTED}" font-size="12" '
        f'text-anchor="middle">{escape(prompt)}</text>\n'
    )


def background_rect(width, height, rx="8"):
    """Build the full-SVG background rectangle."""
    return f'<rect width="{width}" height="{height}" fill="{BG}" rx="{rx}"/>'
