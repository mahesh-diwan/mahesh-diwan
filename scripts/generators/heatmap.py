#!/usr/bin/env python3
"""Render GitHub contribution data as an animated SVG heatmap.

Reads contribution data and writes an animated heatmap SVG.
Each cell slides in with a staggered CSS animation.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from core.svg import background_rect, svg_header, title_bar

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL_W = 14
CELL_H = 14
CELL_GAP = 3
WEEKS = 53
DAYS = 7
MARGIN = 24
WIDTH = MARGIN * 2 + WEEKS * (CELL_W + CELL_GAP)
HEIGHT = MARGIN * 2 + DAYS * (CELL_H + CELL_GAP) + 40 + 32


def render(
    data: dict | None = None, output_path: str = "assets/contrib-heatmap.svg"
) -> None:
    """Build the contribution heatmap SVG from JSON data."""
    if data is None:
        cache_path = Path("data/contributions.json")
        if not cache_path.exists():
            print("No contribution data; writing empty heatmap")
            data = {"days": [], "total_contributions": 0}
        else:
            with open(cache_path) as f:
                data = json.load(f)

    days = data.get("days", [])
    total = data.get("total_contributions", 0)

    if not days:
        base_date = datetime.now(timezone.utc)
    else:
        base_date = datetime.strptime(days[0]["date"], "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )

    grid = [[0] * WEEKS for _ in range(DAYS)]
    for d in days:
        date_obj = datetime.strptime(d["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
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

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg_parts))

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    render()
