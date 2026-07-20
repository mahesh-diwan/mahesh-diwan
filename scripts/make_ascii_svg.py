#!/usr/bin/env python3
"""Convert a prepped grayscale image to an animated ASCII-art SVG.

Reads a grayscale PNG, maps pixel brightness to ASCII characters, and
writes an SVG with per-row clip-path reveal animation and a moving cursor.

Usage::

    python scripts/make_ascii_svg.py
"""

from PIL import Image
import numpy as np

RAMP = " .`:-=+*cs#%@"


def make_ascii(
    input_path="assets/source-prepped.png",
    output_path="assets/mahesh-ascii.svg",
    width_chars=70,
):
    """Generate an animated ASCII SVG from a grayscale image.

    Each row is revealed via a clip-path animation with a moving cursor
    dot, producing a terminal "typing" effect.

    Args:
        input_path: Path to the prepped grayscale PNG.
        output_path: Where to write the output SVG.
        width_chars: Character width of the ASCII grid. Height is
            computed to preserve aspect ratio.
    """
    img = Image.open(input_path).convert("L")

    ramp = RAMP

    char_w = 8
    char_h = 14
    w, h = img.size
    # Correct aspect ratio calculations based on font width/height
    height_chars = int((h / w) * width_chars * (char_w / char_h))
    img = img.resize((width_chars, height_chars), Image.LANCZOS)
    pixels = np.array(img)

    ascii_rows = []
    for row in pixels:
        ascii_row = ""
        for pixel in row:
            idx = int((pixel / 255) * (len(ramp) - 1))
            idx = max(0, min(idx, len(ramp) - 1))
            ascii_row += ramp[idx]
        ascii_rows.append(ascii_row)

    svg_w = width_chars * char_w + 40
    svg_h = height_chars * char_h + 40 + 32

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
        "<defs>",
        "  <style>",
        '    @import url("https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&amp;family=Geist+Mono:wght@400;700&amp;display=swap");',
        '    text { font-family: "Geist Mono", "DM Mono", "Fira Code", ui-monospace, SFMono-Regular, SF Mono, Menlo, Monaco, Consolas, monospace; }',
        "  </style>",
        '  <linearGradient id="ascii-gradient" x1="0%" y1="0%" x2="0%" y2="100%">',
        '    <stop offset="0%" stop-color="#58a6ff" />',
        '    <stop offset="50%" stop-color="#ab7df8" />',
        '    <stop offset="100%" stop-color="#3fb950" />',
        "  </linearGradient>",
        "</defs>",
        '<rect width="100%" height="100%" fill="#0d1117" rx="8"/>',
        f'<rect x="0" y="0" width="{svg_w}" height="32" fill="#161b22" rx="8"/>',
        f'<circle cx="16" cy="16" r="6" fill="#ff5f56"/>',
        f'<circle cx="36" cy="16" r="6" fill="#ffbd2e"/>',
        f'<circle cx="56" cy="16" r="6" fill="#27c93f"/>',
        f'<text x="{svg_w // 2}" y="22" fill="#8b949e" font-size="12" text-anchor="middle">mahesh@portrait:~ $ ./avatar.sh</text>',
        "<style>",
        "  .ascii-text { font-size: 12px; fill: url(#ascii-gradient); font-weight: bold; }",
        "</style>",
    ]

    for i, row in enumerate(ascii_rows):
        y = 24 + 32 + i * char_h
        clip_id = f"clip_{i}"
        delay = i * 0.06
        duration = 0.5

        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(
            f'  <rect x="0" y="{y - char_h}" width="{svg_w}" height="{char_h + 2}">'
        )
        svg_parts.append(
            f'    <animate attributeName="width" from="0" to="{svg_w}" begin="{delay}s" dur="{duration}s" fill="freeze"/>'
        )
        svg_parts.append(f"  </rect>")
        svg_parts.append(f"</clipPath>")

        escaped_row = (
            row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        svg_parts.append(
            f'<text x="20" y="{y}" class="ascii-text" clip-path="url(#{clip_id})">{escaped_row}</text>'
        )

        cursor_x = svg_w - 20
        svg_parts.append(f'<circle r="2" fill="#58a6ff" opacity="0">')
        svg_parts.append(
            f'  <animate attributeName="cx" from="20" to="{cursor_x}" begin="{delay}s" dur="{duration}s" fill="freeze"/>'
        )
        svg_parts.append(
            f'  <animate attributeName="cy" values="{y - 4};{y - 4}" begin="{delay}s" dur="{duration}s" fill="freeze"/>'
        )
        svg_parts.append(
            f'  <animate attributeName="opacity" from="1" to="0" begin="{delay + duration}s" dur="0.1s" fill="freeze"/>'
        )
        svg_parts.append(f"</circle>")

    svg_parts.append("</svg>")

    with open(output_path, "w") as f:
        f.write("\n".join(svg_parts))

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    make_ascii()
