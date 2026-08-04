#!/usr/bin/env python3
"""Convert a prepped grayscale image to an animated ASCII-art SVG.

Reads a grayscale PNG, maps pixel brightness to ASCII characters, and
writes an SVG with per-row clip-path reveal animation and a moving cursor.
"""

from pathlib import Path

import numpy as np
from core.svg import background_rect, escape, svg_header, title_bar
from core.theme import THEME
from PIL import Image

RAMP = " .`:-=+*cs#%@"
CHAR_W = 8
CHAR_H = 14


def render(
    input_path: str = "assets/source-prepped.png",
    output_path: str = "assets/mahesh-ascii.svg",
    width_chars: int = 70,
) -> None:
    """Generate an animated ASCII SVG from a grayscale image."""
    img = Image.open(input_path).convert("L")
    w, h = img.size
    height_chars = int((h / w) * width_chars * (CHAR_W / CHAR_H))
    img = img.resize((width_chars, height_chars), Image.LANCZOS)
    pixels = np.array(img)

    ascii_rows = []
    for row in pixels:
        ascii_row = ""
        for pixel in row:
            idx = int((pixel / 255) * (len(RAMP) - 1))
            idx = max(0, min(idx, len(RAMP) - 1))
            ascii_row += RAMP[idx]
        ascii_rows.append(ascii_row)

    svg_w = width_chars * CHAR_W + 40
    svg_h = height_chars * CHAR_H + 40 + 32

    svg_parts = [
        svg_header(
            svg_w,
            svg_h,
            extra_defs=(
                "  <style>\n"
                "    .ascii-text { font-size: 12px; fill: url(#ascii-gradient); font-weight: bold; }\n"
                "  </style>\n"
                '  <linearGradient id="ascii-gradient" x1="0%" y1="0%" x2="0%" y2="100%">\n'
                f'    <stop offset="0%" stop-color="{THEME.cyan}" />\n'
                '    <stop offset="50%" stop-color="#ab7df8" />\n'
                f'    <stop offset="100%" stop-color="{THEME.green}" />\n'
                "  </linearGradient>"
            ),
        ),
        background_rect(svg_w, svg_h),
        title_bar(svg_w, "mahesh@portrait:~ $ ./avatar.sh"),
    ]

    for i, row in enumerate(ascii_rows):
        y = 24 + 32 + i * CHAR_H
        clip_id = f"clip_{i}"
        delay = i * 0.06
        duration = 0.5

        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(
            f'  <rect x="0" y="{y - CHAR_H}" width="{svg_w}" height="{CHAR_H + 2}">'
        )
        svg_parts.append(
            f'    <animate attributeName="width" from="0" to="{svg_w}" begin="{delay}s" dur="{duration}s" fill="freeze"/>'
        )
        svg_parts.append("  </rect>")
        svg_parts.append("</clipPath>")

        escaped_row = escape(row)
        svg_parts.append(
            f'<text x="20" y="{y}" class="ascii-text" clip-path="url(#{clip_id})">{escaped_row}</text>'
        )

        cursor_x = svg_w - 20
        svg_parts.append(f'<circle r="2" fill="{THEME.cyan}" opacity="0">')
        svg_parts.append(
            f'  <animate attributeName="cx" from="20" to="{cursor_x}" begin="{delay}s" dur="{duration}s" fill="freeze"/>'
        )
        svg_parts.append(
            f'  <animate attributeName="cy" values="{y - 4};{y - 4}" begin="{delay}s" dur="{duration}s" fill="freeze"/>'
        )
        svg_parts.append(
            f'  <animate attributeName="opacity" from="1" to="0" begin="{delay + duration}s" dur="0.1s" fill="freeze"/>'
        )
        svg_parts.append("</circle>")

    svg_parts.append("</svg>")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg_parts))

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    render()
