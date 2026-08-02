#!/usr/bin/env python3
"""Render GitHub contribution data as an animated SVG heatmap.

Reads ``data/contributions.json`` (produced by ``fetch_contributions.py``)
and writes an animated heatmap SVG to ``assets/contrib-heatmap.svg``.

Each cell slides in with a staggered CSS animation. Includes a legend
and total contribution count.

Usage::

    python scripts/render_heatmap_svg.py
"""

import json
import os
from datetime import datetime

from svg_builder import svg_header, title_bar, background_rect

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL_W = 14
CELL_H = 14
CELL_GAP = 3
WEEKS = 53
DAYS = 7
MARGIN = 24

WIDTH = MARGIN * 2 + WEEKS * (CELL_W + CELL_GAP)
HEIGHT = MARGIN * 2 + DAYS * (CELL_H + CELL_GAP) + 40 + 32


def render():
    """Build the contribution heatmap SVG from JSON data.

    Reads contribution days, maps them to a week/day grid, and writes
    an SVG with animated cells and a Less/More legend.

    Raises:
        FileNotFoundError: If ``data/contributions.json`` does not exist.
    """
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json") as f:
        data = json.load(f)

    days = data.get("days", [])
    total = data.get("total_contributions", 0)

    if not days:
        print("No contribution data; writing empty heatmap")
        days = []
        base_date = datetime.now()
    else:
        base_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")

    grid = [[0] * WEEKS for _ in range(DAYS)]
    for d in days:
        dt = d["date"]
        date_obj = datetime.strptime(dt, "%Y-%m-%d")
        week = (date_obj - base_date).days // 7
        dow = date_obj.weekday()
        if 0 <= week < WEEKS and 0 <= dow < DAYS:
            grid[dow][week] = d["level"]

    svg_parts = [
        svg_header(
            WIDTH,
            HEIGHT,
            extra_defs=(
                "    .cell { rx: 3; ry: 3; }\n"
                "    @keyframes slideIn {\n"
                "      from { opacity: 0; transform: translateY(-12px); }\n"
                "      to   { opacity: 1; transform: translateY(0); }\n"
                "    }\n"
                "    .anim-cell {\n"
                "      animation: slideIn 0.4s ease-out forwards;\n"
                "      opacity: 0;\n"
                "    }"
            ),
        ),
        background_rect(WIDTH, HEIGHT),
        title_bar(WIDTH, "mahesh@contributions:~ $ ./contributions.sh"),
    ]

    for dow in range(DAYS):
        for week in range(WEEKS):
            level = grid[dow][week]
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = MARGIN + week * (CELL_W + CELL_GAP)
            y = MARGIN + dow * (CELL_H + CELL_GAP) + 32
            delay = (dow + week) * 0.015
            svg_parts.append(
                f'  <rect class="anim-cell cell" x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" '
                f'fill="{color}" style="animation-delay: {delay:.3f}s"/>'
            )

    legend_y = HEIGHT - 50
    svg_parts.append(
        f'<text x="{MARGIN}" y="{legend_y}" fill="#8b949e" font-size="11">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        lx = MARGIN + 35 + i * 18
        svg_parts.append(
            f'  <rect x="{lx}" y="{legend_y - 9}" width="12" height="12" rx="3" fill="{color}"/>'
        )
    svg_parts.append(
        f'<text x="{MARGIN + 35 + len(PALETTE) * 18 + 6}" y="{legend_y}" fill="#8b949e" font-size="11">More</text>'
    )

    svg_parts.append(
        f'<text x="{WIDTH - MARGIN}" y="{legend_y}" fill="#8b949e" font-size="11" '
        f'text-anchor="end">{total:,} contributions in the last year</text>'
    )

    svg_parts.append("</svg>")

    with open("assets/contrib-heatmap.svg", "w") as f:
        f.write("\n".join(svg_parts))

    print("Wrote assets/contrib-heatmap.svg")


if __name__ == "__main__":
    render()
