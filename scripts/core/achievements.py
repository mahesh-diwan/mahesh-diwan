"""Achievement rules — pure functions over a GitHub profile dict.

Each rule is a simple threshold check over data that already exists in the
profile dict produced by core.github.fetch_profile(). No invented metrics.
"""

CLOUD_LANGS = {"HCL", "YAML", "Dockerfile", "Go", "Bash"}

ACHIEVEMENTS = [
    {"id": "ship_it", "emoji": "🚢", "name": "Ship It"},
    {"id": "streak_lord", "emoji": "🔥", "name": "Streak Lord"},
    {"id": "night_owl", "emoji": "🦉", "name": "Night Owl"},
    {"id": "star_surfer", "emoji": "⭐", "name": "Star Surfer"},
    {"id": "builder", "emoji": "🧱", "name": "Builder"},
    {"id": "cloud_arch", "emoji": "☁️", "name": "Multi-cloud"},
    {"id": "veteran", "emoji": "⏳", "name": "Veteran"},
]


def _cloud_lang_count(profile: dict) -> int:
    langs = {lang["name"] for lang in profile.get("languages") or []}
    return len(langs & CLOUD_LANGS)


def _check(achievement_id: str, profile: dict) -> bool:
    if achievement_id == "ship_it":
        return (profile.get("merged_prs") or 0) >= 50
    if achievement_id == "streak_lord":
        return (profile.get("longest_streak") or 0) >= 30
    if achievement_id == "night_owl":
        return (profile.get("current_streak") or 0) >= 14
    if achievement_id == "star_surfer":
        return (profile.get("stars") or 0) >= 100
    if achievement_id == "builder":
        return (profile.get("repos") or 0) >= 5
    if achievement_id == "cloud_arch":
        return _cloud_lang_count(profile) >= 2
    if achievement_id == "veteran":
        return (profile.get("years") or 0) >= 2
    return False


def compute_achievements(profile: dict) -> list[dict]:
    """Return each achievement tagged with whether the profile earns it."""
    return [
        {**achievement, "earned": _check(achievement["id"], profile)}
        for achievement in ACHIEVEMENTS
    ]
