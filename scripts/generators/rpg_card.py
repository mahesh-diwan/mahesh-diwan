#!/usr/bin/env python3
"""Generate an RPG character card SVG from GitHub activity.

Maps languages to classes, commits to XP, PRs to quests completed.
Animated SVG with glow effects, XP bar, and rarity tiers.
"""

import math
import os
from pathlib import Path

from core.github import fetch_profile
from core.svg import background_rect, escape, svg_header
from core.theme import THEME

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
    """Compute RPG character stats from GitHub profile data.

    XP formula:
        craftXP = commits*10 + issues*30 + PRs*65 + reviews*40 + repos*120
        tenureMult = 1 + min(years, 15) * 0.05
        comboMult = 1 + min(streak, 365) / 365 * 0.25
        streakXP = streak * 8
        fameXP = min(40000, 48 * sqrt(followers + stars))
        totalXP = craftXP * tenureMult * comboMult + streakXP + fameXP
        level = floor(sqrt(totalXP / 100))
    """
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

    # XP to next level
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


def render(
    output_path: str = "assets/rpg-card.svg",
    token: str | None = None,
) -> None:
    """Generate the RPG character card SVG."""
    profile = fetch_profile(token=token)
    char = compute_character(profile)

    width = 500
    height = 320

    # XP bar dimensions
    bar_x, bar_y, bar_w, bar_h = 20, 130, 460, 16
    fill_w = int(bar_w * char["progress"])

    # Language bar
    lang_y = 230
    lang_colors = {
        "Python": "#3572A5",
        "Bash": "#89e051",
        "Go": "#00ADD8",
        "JavaScript": "#f1e05a",
        "TypeScript": "#3178c6",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Dockerfile": "#384d54",
        "YAML": "#cb171e",
        "HCL": "#844FBA",
        "Java": "#b07219",
        "C++": "#f34b7d",
        "Rust": "#dea584",
        "Ruby": "#701516",
    }

    svg_parts = [
        svg_header(
            width,
            height,
            extra_defs=(
                f'<filter id="glow">'
                f'<feGaussianBlur stdDeviation="3" result="blur"/>'
                f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
                f"</filter>"
                "<style>"
                "  @keyframes pulse { 0%,100%{opacity:0.6} 50%{opacity:1} }"
                "  @keyframes barGrow { from{width:0} }"
                "  @keyframes fadeSlide { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }"
                "  .stat { animation: fadeSlide 0.4s ease-out forwards; opacity: 0; }"
                "  .bar-fill { animation: barGrow 1s ease-out forwards; }"
                "  .glow { animation: pulse 2s ease-in-out infinite; }"
                "</style>"
            ),
        ),
        background_rect(width, height),
    ]

    # Title bar (no traffic lights — RPG card has its own style)
    svg_parts.append(
        f'<rect x="0" y="0" width="{width}" height="32" fill="{THEME.surface}" rx="8"/>'
        f'<text x="{width // 2}" y="22" fill="{THEME.muted}" font-size="12" '
        f'text-anchor="middle">mahesh@github:~ $ cat ~/.class</text>'
    )

    # Character name + class
    svg_parts.append(
        f'<text x="20" y="60" fill="{THEME.fg}" font-size="20" font-weight="bold" '
        f'class="stat" style="animation-delay:0.1s">{escape(char["name"])}</text>'
    )
    svg_parts.append(
        f'<text x="20" y="80" fill="{char["rarity_color"]}" font-size="13" font-weight="bold" '
        f'class="stat" style="animation-delay:0.2s">{escape(char["class_name"])} — Level {char["level"]}</text>'
    )
    svg_parts.append(
        f'<text x="20" y="98" fill="{THEME.muted}" font-size="11" '
        f'class="stat" style="animation-delay:0.25s">{escape(char["class_desc"])}</text>'
    )

    # Rarity badge
    badge_x = width - 100
    svg_parts.append(
        f'<rect x="{badge_x}" y="45" width="80" height="24" rx="12" '
        f'fill="{char["rarity_color"]}" opacity="0.2" class="glow"/>'
        f'<text x="{badge_x + 40}" y="61" fill="{char["rarity_color"]}" font-size="11" '
        f'font-weight="bold" text-anchor="middle">{escape(char["rarity"])}</text>'
    )

    # XP bar
    svg_parts.append(
        f'<text x="20" y="124" fill="{THEME.muted}" font-size="11">'
        f"XP {char['total_xp']:,} / {((char['level'] + 1) ** 2) * 100:,}</text>"
    )
    svg_parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
        f'rx="4" fill="{THEME.xp_bg}"/>'
    )
    svg_parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{fill_w}" height="{bar_h}" '
        f'rx="4" fill="{THEME.xp_fill}" class="bar-fill" filter="url(#glow)"/>'
    )
    svg_parts.append(
        f'<text x="{bar_x + bar_w - 4}" y="{bar_y + 12}" fill="{THEME.fg}" font-size="10" '
        f'text-anchor="end">{int(char["progress"] * 100)}%</text>'
    )

    # Stats grid (2 columns, 3 rows)
    stats = [
        ("Commits", f"{char['commits']:,}", 0.3),
        ("PRs Merged", f"{char['prs']:,}", 0.35),
        ("Reviews", f"{char['reviews']:,}", 0.4),
        ("Issues", f"{char['issues']:,}", 0.45),
        ("Repos", f"{char['repos']:,}", 0.5),
        ("Stars", f"{char['stars']:,}", 0.55),
    ]

    for i, (label, value, delay) in enumerate(stats):
        col = i % 2
        row = i // 2
        sx = 20 + col * 240
        sy = 170 + row * 22

        svg_parts.append(
            f'<text x="{sx}" y="{sy}" fill="{THEME.muted}" font-size="11" '
            f'class="stat" style="animation-delay:{delay}s">{label}</text>'
        )
        svg_parts.append(
            f'<text x="{sx + 140}" y="{sy}" fill="{THEME.cyan}" font-size="11" font-weight="bold" '
            f'text-anchor="end" class="stat" style="animation-delay:{delay + 0.05}s">{value}</text>'
        )

    # Streak info
    svg_parts.append(
        f'<text x="20" y="{lang_y - 10}" fill="{THEME.muted}" font-size="11">'
        f"Streak: {char['streak']}d current / {char['longest_streak']}d best</text>"
    )

    # Language bars
    total_bytes = sum(l["bytes"] for l in char["languages"]) or 1
    bar_x_offset = 20
    bar_width_total = width - 40

    for lang in char["languages"][:5]:
        pct = lang["bytes"] / total_bytes
        w = max(int(bar_width_total * pct), 8)
        color = lang_colors.get(lang["name"], THEME.muted)
        svg_parts.append(
            f'<rect x="{bar_x_offset}" y="{lang_y}" width="{w}" height="8" '
            f'rx="2" fill="{color}" opacity="0.8"/>'
        )
        bar_x_offset += w + 2

    # Language labels
    labels_x = 20
    for lang in char["languages"][:5]:
        pct = lang["bytes"] / total_bytes * 100
        color = lang_colors.get(lang["name"], THEME.muted)
        svg_parts.append(
            f'<text x="{labels_x}" y="{lang_y + 22}" fill="{color}" font-size="10">'
            f"{escape(lang['name'])} {pct:.0f}%</text>"
        )
        labels_x += len(lang["name"]) * 7 + 40

    # Footer
    svg_parts.append(
        f'<text x="{width // 2}" y="{height - 12}" fill="{THEME.muted}" font-size="9" '
        f'text-anchor="middle">Generated from {escape(char["login"])}\'s GitHub activity</text>'
    )

    svg_parts.append("</svg>")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg_parts))

    print(
        f"Wrote {output_path} — {char['class_name']} Level {char['level']} ({char['rarity']})"
    )


if __name__ == "__main__":
    render()
