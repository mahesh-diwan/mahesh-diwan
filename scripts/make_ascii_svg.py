#!/usr/bin/env python3
"""
Convert prepped image to animated ASCII SVG.
"""
import sys
from PIL import Image
import numpy as np

RAMP = " .`:-=+*cs#%@"

def make_ascii(input_path="assets/source-prepped.png", output_path="assets/mahesh-ascii.svg", width_chars=70):
    img = Image.open(input_path).convert("L")

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
            idx = int((pixel / 255) * (len(RAMP) - 1))
            idx = max(0, min(idx, len(RAMP) - 1))
            ascii_row += RAMP[idx]
        ascii_rows.append(ascii_row)

    svg_w = width_chars * char_w + 40
    svg_h = height_chars * char_h + 40

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
        '<defs>',
        '  <linearGradient id="ascii-gradient" x1="0%" y1="0%" x2="0%" y2="100%">',
        '    <stop offset="0%" stop-color="#58a6ff" />',
        '    <stop offset="50%" stop-color="#ab7df8" />',
        '    <stop offset="100%" stop-color="#3fb950" />',
        '  </linearGradient>',
        '</defs>',
        '<rect width="100%" height="100%" fill="#0d1117" rx="8"/>',
        '<style>',
        '  .ascii-text { font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Monaco, Consolas, monospace; font-size: 12px; fill: url(#ascii-gradient); font-weight: bold; }',
        '</style>',
    ]

    for i, row in enumerate(ascii_rows):
        y = 24 + i * char_h
        clip_id = f"clip_{i}"
        delay = i * 0.08
        duration = 0.6

        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(f'  <rect x="0" y="{y - char_h}" width="0" height="{char_h + 2}">')
        svg_parts.append(f'    <animate attributeName="width" from="0" to="{svg_w}" begin="{delay}s" dur="{duration}s" fill="freeze"/>')
        svg_parts.append(f'  </rect>')
        svg_parts.append(f'</clipPath>')

        escaped_row = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        svg_parts.append(f'<text x="20" y="{y}" class="ascii-text" clip-path="url(#{clip_id})">{escaped_row}</text>')

        cursor_x = svg_w - 20
        svg_parts.append(f'<circle r="2" fill="#58a6ff" opacity="0">')
        svg_parts.append(f'  <animate attributeName="cx" from="20" to="{cursor_x}" begin="{delay}s" dur="{duration}s" fill="freeze"/>')
        svg_parts.append(f'  <animate attributeName="cy" values="{y - 4};{y - 4}" begin="{delay}s" dur="{duration}s" fill="freeze"/>')
        svg_parts.append(f'  <animate attributeName="opacity" from="1" to="0" begin="{delay + duration}s" dur="0.1s" fill="freeze"/>')
        svg_parts.append(f'</circle>')

    svg_parts.append('</svg>')

    with open(output_path, "w") as f:
        f.write("\n".join(svg_parts))

    print(f"Wrote {output_path}")

if __name__ == "__main__":
    make_ascii()
