#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG.
Set STATIC=1 for a frozen frame (no animation).
"""
import os

STATIC = os.environ.get("STATIC", "0") == "1"

WIDTH = 490
HEIGHT = 420
BG = "#0d1117"
FG = "#c9d1d9"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
YELLOW = "#d29922"
PURPLE = "#a371f7"
RED = "#f85149"

TITLE = "mahesh-diwan"
LINES = [
    ("Name", "Mahesh Diwan"),
    ("Role", "Computer Engineering Student"),
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


def render():
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<defs>',
        '  <style>',
        '    @import url("https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&amp;family=Geist+Mono:wght@400;700&amp;display=swap");',
        '    text {',
        '      font-family: "Geist Mono", "DM Mono", "Fira Code", ui-monospace, SFMono-Regular, SF Mono, Menlo, Monaco, Consolas, monospace;',
        '    }',
        '  </style>',
        '</defs>',
        f'<rect width="100%" height="100%" fill="{BG}" rx="8"/>',
    ]

    if not STATIC:
        svg_parts.append('<style>')
        svg_parts.append('  @keyframes fadeSlide {')
        svg_parts.append('    from { opacity: 0; transform: translateX(-10px); }')
        svg_parts.append('    to   { opacity: 1; transform: translateX(0); }')
        svg_parts.append('  }')
        svg_parts.append('  .line {')
        svg_parts.append('    animation: fadeSlide 0.35s ease-out forwards;')
        svg_parts.append('    opacity: 0;')
        svg_parts.append('  }')
        svg_parts.append('</style>')

    # Title bar
    svg_parts.append(f'<rect x="0" y="0" width="{WIDTH}" height="32" fill="#161b22" rx="8"/>')
    svg_parts.append(f'<circle cx="16" cy="16" r="6" fill="#ff5f56"/>')
    svg_parts.append(f'<circle cx="36" cy="16" r="6" fill="#ffbd2e"/>')
    svg_parts.append(f'<circle cx="56" cy="16" r="6" fill="#27c93f"/>')
    svg_parts.append(f'<text x="{WIDTH//2}" y="22" fill="#8b949e" font-size="12" text-anchor="middle">{TITLE}</text>')

    # Content lines
    y = 56
    delay = 0.1
    for key, value in LINES:
        if key == "" and value == "":
            y += 8
            continue

        style = '' if STATIC else f' class="line" style="animation-delay: {delay:.2f}s"'
        if key.startswith("  "):
            k = key.strip()
            svg_parts.append(
                f'<text x="28" y="{y}" fill="{ACCENT}" font-size="12" font-weight="bold"{style}>{k}</text>'
            )
            if value:
                svg_parts.append(
                    f'<text x="110" y="{y}" fill="{FG}" font-size="12"{style}>{escape(value)}</text>'
                )
        elif value == "":
            svg_parts.append(
                f'<text x="20" y="{y}" fill="{GREEN}" font-size="13" font-weight="bold"{style}>{escape(key)}</text>'
            )
        else:
            svg_parts.append(
                f'<text x="20" y="{y}" fill="{YELLOW}" font-size="12" font-weight="bold"{style}>{escape(key)}</text>'
            )
            svg_parts.append(
                f'<text x="110" y="{y}" fill="{FG}" font-size="12"{style}>{escape(value)}</text>'
            )

        y += 20
        delay += 0.08

    svg_parts.append('</svg>')

    with open("assets/info-card.svg", "w") as f:
        f.write("\n".join(svg_parts))

    print("Wrote assets/info-card.svg")


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    render()
