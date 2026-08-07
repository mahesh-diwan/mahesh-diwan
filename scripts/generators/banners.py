#!/usr/bin/env python3
"""Generate theme-matched SVG section headers for the profile README."""

from pathlib import Path

from core.svg import background_rect, escape, svg_header
from core.theme import THEME

WIDTH = 760
HEIGHT = 44
FONT_SIZE = 20
# Mono char advance at font-size 20 (0.6em)
ADVANCE = 12
X0 = 16
Y0 = 28

# slug -> list of (text, color) segments rendered left-to-right
BANNERS = {
    "status": [("✓ status: currently refactoring flexfetch", THEME.muted)],
    "arcade": [("mahesh@github ~ $ ", THEME.cyan), ("./arcade.sh", THEME.fg)],
    "ssh": [
        ("mahesh@github ~ $ ", THEME.cyan),
        ("cat ~/.ssh/authorized_keys", THEME.fg),
    ],
    "activity": [("📜 Recent activity", THEME.fg)],
    "projects": [("📦 Featured projects", THEME.fg)],
    "blog": [("✍️ Blog posts", THEME.fg)],
    "agents": [("🤖 For agents", THEME.fg)],
}


def build_banner(segments: list[tuple[str, str]]) -> str:
    """Build one banner SVG (pure — no I/O)."""
    parts = [svg_header(WIDTH, HEIGHT), background_rect(WIDTH, HEIGHT)]
    x = X0
    for text, color in segments:
        parts.append(
            f'<text x="{x}" y="{Y0}" fill="{color}" font-size="{FONT_SIZE}">'
            f"{escape(text)}</text>"
        )
        x += ADVANCE * len(text)
    parts.append("</svg>")
    return "\n".join(parts)


def render(output_dir: str = "assets") -> None:
    """Write all banner SVGs to output_dir."""
    for slug, segments in BANNERS.items():
        out = Path(output_dir) / f"header-{slug}.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_banner(segments))
        print(f"Wrote {out}")


if __name__ == "__main__":
    render()
