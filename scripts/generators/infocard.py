#!/usr/bin/env python3
"""Generate a neofetch-style info card SVG.

Renders terminal-style profile information as an SVG with staggered
fade-slide animations. Set ``STATIC=1`` env var for a frozen frame.
"""

import os
from pathlib import Path

from core.svg import background_rect, escape, svg_header, title_bar
from core.theme import THEME

STATIC = os.environ.get("STATIC", "0") == "1"

WIDTH = 490
HEIGHT = 420
TITLE = "mahesh@neofetch:~ $ whoami"
LINES = [
    ("Name", "Mahesh Diwan"),
    ("Role", "DevOps Engineer"),
    ("Focus", "DevOps | Cloud | Automation"),
    ("Location", "India"),
    ("", ""),
    ("Learning", ""),
    ("  Now", "Kubernetes, Jenkins, Terraform"),
    ("  Stack", "Python, JavaScript, C++, Java, Go"),
    ("", ""),
    ("Tools", ""),
    ("  Cloud", "AWS"),
    ("  Container", "Docker, Kubernetes"),
    ("  CI/CD", "Jenkins, GitHub Actions"),
    ("  OS", "Linux"),
    ("  VCS", "Git, Bash"),
    ("", ""),
    ("Projects", ""),
    ("  DeskTap", "github.com/mahesh-diwan/DeskTap"),
    ("", ""),
    ("Blog", "mahesh1215.hashnode.dev"),
    ("Resume", "drive.google.com/... (see profile)"),
]


def render(output_path: str = "assets/info-card.svg") -> None:
    """Build the info-card SVG."""
    svg_parts = [
        svg_header(WIDTH, HEIGHT),
        background_rect(WIDTH, HEIGHT),
    ]

    if not STATIC:
        svg_parts.append("<style>")
        svg_parts.append("  @keyframes fadeSlide {")
        svg_parts.append("    from { opacity: 0; transform: translateX(-10px); }")
        svg_parts.append("    to   { opacity: 1; transform: translateX(0); }")
        svg_parts.append("  }")
        svg_parts.append("  .line {")
        svg_parts.append("    animation: fadeSlide 0.35s ease-out forwards;")
        svg_parts.append("    opacity: 0;")
        svg_parts.append("  }")
        svg_parts.append("</style>")

    svg_parts.append(title_bar(WIDTH, TITLE))

    y = 56
    delay = 0.1
    for key, value in LINES:
        if key == "" and value == "":
            y += 8
            continue

        style = "" if STATIC else f' class="line" style="animation-delay: {delay:.2f}s"'
        if key.startswith("  "):
            k = key.strip()
            svg_parts.append(
                f'<text x="28" y="{y}" fill="{THEME.cyan}" font-size="12" font-weight="bold"{style}>{k}</text>'
            )
            if value:
                svg_parts.append(
                    f'<text x="110" y="{y}" fill="{THEME.fg}" font-size="12"{style}>{escape(value)}</text>'
                )
        elif value == "":
            svg_parts.append(
                f'<text x="20" y="{y}" fill="{THEME.green}" font-size="13" font-weight="bold"{style}>{escape(key)}</text>'
            )
        else:
            svg_parts.append(
                f'<text x="20" y="{y}" fill="{THEME.yellow}" font-size="12" font-weight="bold"{style}>{escape(key)}</text>'
            )
            svg_parts.append(
                f'<text x="110" y="{y}" fill="{THEME.fg}" font-size="12"{style}>{escape(value)}</text>'
            )

        y += 20
        delay += 0.08

    svg_parts.append("</svg>")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg_parts))

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    render()
