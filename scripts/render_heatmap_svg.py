#!/usr/bin/env python3
"""
Render contributions.json as an animated SVG heatmap.
"""
import json
import os

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL_W = 14
CELL_H = 14
CELL_GAP = 3
WEEKS = 53
DAYS = 7
MARGIN = 24

WIDTH = MARGIN * 2 + WEEKS * (CELL_W + CELL_GAP)
HEIGHT = MARGIN * 2 + DAYS * (CELL_H + CELL_GAP) + 40


def render():
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json") as f:
        data = json.load(f)

    days = data["days"]
    total = data.get("total_contributions", 0)

    grid = [[0] * WEEKS for _ in range(DAYS)]
    for d in days:
        from datetime import datetime
        dt = d["date"]
        date_obj = datetime.strptime(dt, "%Y-%m-%d")
        week = (date_obj - datetime.strptime(days[0]["date"], "%Y-%m-%d")).days // 7
        dow = date_obj.weekday()
        if 0 <= week < WEEKS and 0 <= dow < DAYS:
            grid[dow][week] = d["level"]

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<style>',
        '  .cell { rx: 3; ry: 3; }',
        '  @keyframes slideIn {',
        '    from { opacity: 0; transform: translateY(-12px); }',
        '    to   { opacity: 1; transform: translateY(0); }',
        '  }',
        '  .anim-cell {',
        '    animation: slideIn 0.4s ease-out forwards;',
        '    opacity: 0;',
        '  }',
        '</style>',
        '<rect width="100%" height="100%" fill="#0d1117"/>',
    ]

    for dow in range(DAYS):
        for week in range(WEEKS):
            level = grid[dow][week]
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = MARGIN + week * (CELL_W + CELL_GAP)
            y = MARGIN + dow * (CELL_H + CELL_GAP)
            delay = (dow + week) * 0.015
            svg_parts.append(
                f'  <rect class="anim-cell cell" x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" '
                f'fill="{color}" style="animation-delay: {delay:.3f}s"/>'
            )

    legend_y = HEIGHT - 50
    svg_parts.append(f'<text x="{MARGIN}" y="{legend_y}" fill="#8b949e" font-size="11" font-family="monospace">Less</text>')
    for i, color in enumerate(PALETTE):
        lx = MARGIN + 35 + i * 18
        svg_parts.append(f'  <rect x="{lx}" y="{legend_y - 9}" width="12" height="12" rx="3" fill="{color}"/>')
    svg_parts.append(f'<text x="{MARGIN + 35 + len(PALETTE) * 18 + 6}" y="{legend_y}" fill="#8b949e" font-size="11" font-family="monospace">More</text>')

    svg_parts.append(
        f'<text x="{WIDTH - MARGIN}" y="{legend_y}" fill="#8b949e" font-size="11" '
        f'font-family="monospace" text-anchor="end">{total:,} contributions in the last year</text>'
    )

    svg_parts.append('</svg>')

    with open("assets/contrib-heatmap.svg", "w") as f:
        f.write("\n".join(svg_parts))

    print("Wrote assets/contrib-heatmap.svg")


if __name__ == "__main__":
    render()
