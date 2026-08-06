#!/usr/bin/env python3
"""Generate the fused profile header SVG.

One compact banner: block-art avatar tile, name, class · rarity, tagline,
achievement pills, and LVL / COMMITS / STREAK chips.
"""

import math
from pathlib import Path

from core.achievements import compute_achievements
from core.github import fetch_profile
from core.svg import background_rect, escape, svg_header
from core.theme import THEME

WIDTH = 760
HEIGHT = 170

# 4x4 block-art avatar, drawn with half-block characters (no external image)
AVATAR_ART = [
    "▚▞▚▞",
    "▞▚▞▚",
    "▚▞▚▞",
    "▞▚▞▚",
]

# === Class system (by primary language) ===
CLASSES = {
    "Python": ("Automancer", "Spellcaster who bends automation to their will"),
    "Bash": ("Scriptlord", "Master of shell incantations"),
    "Go": ("Gopher Knight", "Fast, concurrent warrior"),
    "JavaScript": ("Web Weaver", "Crafts interactive experiences"),
    "TypeScript": ("Type Sage", "Strongly typed sorcerer"),
    "HTML": ("Markup Mage", "Architect of structure"),
    "CSS": ("Style Oracle", "Weaver of visual magic"),
    "Dockerfile": ("Container Mage", "Encapsulates worlds in layers"),
    "YAML": ("Config Whisper", "Shapes infrastructure with words"),
    "HCL": ("Terraform Architect", "Builds clouds from code"),
    "Shell": ("Scriptlord", "Master of shell incantations"),
    "Makefile": ("Build Master", "Orchestrates compilation"),
    "Java": ("Bytecode Paladin", "Cross-platform champion"),
    "C++": ("Memory Wizard", "Direct hardware whisperer"),
    "Rust": ("Iron Guardian", "Safe and fearless"),
    "Ruby": ("Gem Sorcerer", "Elegant magic"),
    "PHP": ("Web Alchemist", "Server-side transmuter"),
}

DEFAULT_CLASS = ("DevOps Sentinel", "Guardian of pipelines and clouds")

# === Rarity tiers (by level) ===
RARITIES = [
    (1, "Common", THEME.rarity_common),
    (10, "Rare", THEME.rarity_rare),
    (25, "Epic", THEME.rarity_epic),
    (50, "Legendary", THEME.rarity_legendary),
    (100, "Mythic", THEME.rarity_mythic),
]


def _get_rarity(level: int) -> tuple[str, str]:
    """Return (name, color) for the given level."""
    result = (RARITIES[0][1], RARITIES[0][2])
    for threshold, name, color in RARITIES:
        if level >= threshold:
            result = (name, color)
    return result


def _get_class(primary_lang: str) -> tuple[str, str]:
    """Return (class_name, description) for the given language."""
    return CLASSES.get(primary_lang, DEFAULT_CLASS)


def compute_character(profile: dict) -> dict:
    """Compute character stats (class, rarity, level) from GitHub profile data."""
    commits = profile["commits"]
    prs = profile["merged_prs"]
    reviews = profile["reviews"]
    issues = profile["closed_issues"]
    repos = profile["repos"]
    stars = profile["stars"]
    followers = profile["followers"]
    streak = profile["current_streak"]
    years = profile["years"]

    craft_xp = commits * 10 + issues * 30 + prs * 65 + reviews * 40 + repos * 120
    tenure_mult = 1 + min(years, 15) * 0.05
    combo_mult = 1 + min(streak, 365) / 365 * 0.25
    streak_xp = streak * 8
    fame_xp = min(40000, 48 * math.sqrt(followers + stars))

    total_xp = craft_xp * tenure_mult * combo_mult + streak_xp + fame_xp
    level = int(math.sqrt(total_xp / 100))

    next_level_xp = ((level + 1) ** 2) * 100
    prev_level_xp = (level**2) * 100
    xp_in_level = total_xp - prev_level_xp
    xp_needed = next_level_xp - prev_level_xp
    progress = min(xp_in_level / xp_needed, 1.0) if xp_needed > 0 else 1.0

    class_name, class_desc = _get_class(profile["primary_language"])
    rarity_name, rarity_color = _get_rarity(level)

    return {
        "name": profile["name"],
        "login": profile["login"],
        "class_name": class_name,
        "class_desc": class_desc,
        "level": level,
        "total_xp": int(total_xp),
        "progress": progress,
        "rarity": rarity_name,
        "rarity_color": rarity_color,
        "commits": commits,
        "prs": prs,
        "reviews": reviews,
        "issues": issues,
        "repos": repos,
        "stars": stars,
        "followers": followers,
        "streak": streak,
        "longest_streak": profile["longest_streak"],
        "primary_language": profile["primary_language"],
        "languages": profile["languages"],
    }


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
    langs = [lang.get("name") for lang in char.get("languages") or []][:3]
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
