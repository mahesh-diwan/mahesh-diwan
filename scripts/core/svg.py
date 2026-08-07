"""Shared SVG builder — thin wrappers over Theme for common markup.

Replaces the old svg_builder.py. Generators import from here.
"""

from xml.sax.saxutils import escape as _xml_escape

from core.theme import THEME


def escape(text: str) -> str:
    """Escape XML special characters for SVG text content."""
    return _xml_escape(str(text))


def svg_header(width: int, height: int, extra_defs: str = "") -> str:
    """Build the opening ``<svg>`` tag with shared font CSS in ``<style>``."""
    css = f"    {THEME.font_css}\n"
    if extra_defs:
        css += f"    {extra_defs}\n"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
        "  <style>\n"
        f"{css}"
        "  </style>\n"
    )


def title_bar(width: int, prompt: str) -> str:
    """Build the macOS-style traffic-light title bar."""
    return (
        f'<rect x="0" y="0" width="{width}" height="32" fill="{THEME.surface}" rx="8"/>\n'
        f'<circle cx="16" cy="16" r="6" fill="{THEME.red}"/>\n'
        f'<circle cx="36" cy="16" r="6" fill="{THEME.yellow}"/>\n'
        f'<circle cx="56" cy="16" r="6" fill="{THEME.green}"/>\n'
        f'<text x="{width // 2}" y="22" fill="{THEME.muted}" font-size="12" '
        f'text-anchor="middle">{escape(prompt)}</text>\n'
    )


def background_rect(width: int, height: int, rx: str = "8") -> str:
    """Build the full-SVG background rectangle."""
    return f'<rect width="{width}" height="{height}" fill="{THEME.bg}" rx="{rx}"/>'
