#!/usr/bin/env python3
"""Generate the fused profile header SVG.

Replaces the old whoami table (mahesh-ascii.svg + info-card.svg): one compact
banner with a block-art avatar tile, name, class · rarity, tagline,
achievement pills, and LVL / COMMITS / STREAK chips.
"""

from pathlib import Path

from core.achievements import compute_achievements
from core.github import fetch_profile
from core.svg import background_rect, escape, svg_header
from core.theme import THEME
from generators.rpg_card import compute_character

WIDTH = 760
HEIGHT = 170

# 4x4 block-art avatar, drawn with half-block characters (no external image)
AVATAR_ART = [
    "▚▞▚▞",
    "▞▚▞▚",
    "▚▞▚▞",
    "▞▚▞▚",
]


def _fade(delay: float) -> str:
    """SMIL fade-in for a text element."""
    return (
        f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" '
        f'begin="{delay}s" fill="freeze"/>'
    )


def _avatar_tile(x: float, y: float) -> str:
    parts = [
        f'<rect x="{x}" y="{y}" width="72" height="72" rx="8" fill="{THEME.surface}"/>'
    ]
    for i, row in enumerate(AVATAR_ART):
        parts.append(
            f'<text x="{x + 8}" y="{y + 18 + i * 15}" fill="{THEME.cyan}" font-size="14">'
            f"{escape(row)}</text>"
        )
    return "".join(parts)


def _chip(x: float, y: float, label: str, value: str) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="86" height="26" rx="13" fill="{THEME.surface}"/>'
        f'<text x="{x + 8}" y="{y + 17}" fill="{THEME.muted}" font-size="10">'
        f"{escape(label)}</text>"
        f'<text x="{x + 80}" y="{y + 17}" fill="{THEME.cyan}" font-size="12" '
        f'font-weight="bold" text-anchor="end">{escape(value)}</text>'
    )


def _pill(x: float, y: float, achievement: dict) -> str:
    text = f"{achievement['emoji']} {achievement['name']}"
    width = 22 + len(text) * 7
    if achievement["earned"]:
        return (
            f'<rect x="{x}" y="{y}" width="{width}" height="24" rx="12" '
            f'fill="{THEME.cyan}" opacity="0.15"/>'
            f'<text x="{x + 8}" y="{y + 16}" fill="{THEME.cyan}" font-size="10">'
            f"{escape(text)}</text>"
        )
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="24" rx="12" '
        f'fill="none" stroke="{THEME.muted}" stroke-dasharray="4 3"/>'
        f'<text x="{x + 8}" y="{y + 16}" fill="{THEME.muted}" font-size="10">'
        f"{escape(text)}</text>"
    )


def _tagline(char: dict) -> str:
    langs = [lang["name"] for lang in char.get("languages") or []][:3]
    desc = char.get("class_desc") or ""
    if langs:
        return " / ".join(langs) + " — " + desc
    primary = char.get("primary_language") or ""
    if primary and primary != "Unknown":
        return primary + " — " + desc
    return desc


def build_header(profile: dict) -> str:
    """Build the complete profile-header SVG as a string (pure, no I/O)."""
    char = compute_character(profile)
    achievements = compute_achievements(profile)

    parts = [svg_header(WIDTH, HEIGHT), background_rect(WIDTH, HEIGHT)]

    parts.append(_avatar_tile(16, 16))

    parts.append(
        f'<text x="104" y="40" fill="{THEME.cyan}" font-size="20" font-weight="bold">'
        f"{_fade(0.1)}{escape(char['name'])}</text>"
    )
    parts.append(
        f'<text x="104" y="62" fill="{char["rarity_color"]}" font-size="13" font-weight="bold">'
        f"{_fade(0.2)}{escape(char['class_name'])} · {escape(char['rarity'])}</text>"
    )
    parts.append(
        f'<text x="104" y="82" fill="{THEME.muted}" font-size="11">'
        f"{_fade(0.3)}{escape(_tagline(char))}</text>"
    )

    chips_x = WIDTH - 20 - 86
    parts.append(_chip(chips_x, 20, "LVL", str(char["level"])))
    parts.append(_chip(chips_x - 94, 20, "COMMITS", f"{char['commits']:,}"))
    parts.append(_chip(chips_x - 188, 20, "STREAK", f"{char['streak']}d"))

    px = 16
    gap = 4
    for achievement in achievements:
        parts.append(_pill(px, 116, achievement))
        px += 22 + len(f"{achievement['emoji']} {achievement['name']}") * 7 + gap

    parts.append(
        f'<text x="{WIDTH // 2}" y="{HEIGHT - 10}" fill="{THEME.muted}" font-size="9" '
        f'text-anchor="middle">github.com/{escape(profile.get("login") or "")}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def render(
    output_path: str = "assets/profile-header.svg",
    profile: dict | None = None,
    token: str | None = None,
) -> None:
    """Write the profile-header SVG. Fetches profile when not supplied."""
    if profile is None:
        profile = fetch_profile(token=token)
    svg = build_header(profile)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(svg)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    render()
