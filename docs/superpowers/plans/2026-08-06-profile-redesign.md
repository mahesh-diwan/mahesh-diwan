# Profile Redesign (A3 Stats Board) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove contribution-graph redundancy and clutter from the GitHub profile README, replacing the `whoami` table with a fused profile header, adding achievements, a status strip, and a recent-activity log, and dropping Breakout.

**Architecture:** Three new pure/testable modules in `scripts/` — `core/achievements.py` (pure rule checks), `generators/header.py` (fused header SVG), `generators/activity.py` (activity log SVG) — wired into the existing `scripts/cli.py` build target and the existing orchestrator workflow. README restructured to the locked top-to-bottom layout.

**Tech Stack:** Python 3.12, pytest (34 existing tests), SMIL-animated SVG (no CSS keyframes, no external @import), GitHub REST + GraphQL APIs, GitHub Actions (`profile-orchestrator.yml`).

## Global Constraints

- **SVG hard requirement:** SMIL-only animation (`<animate>`, `<animateTransform>`, `<set>`). NO CSS `@keyframes`, NO external `@import`, NO `fonts.googleapis.com` references inside SVG — GitHub's `<img>` renderer blocks external resources and fails to decode the whole SVG when present (verified in prior sessions; `scripts/core/theme.py` already strips the font `@import`).
- **Palette locked** (verbatim): bg `#0d1117`, surface `#161b22`, borders/xp-bg `#21262d`, fg `#c9d1d9`, muted `#8b949e`, accent `#00D4FF`. Do not introduce new colors.
- **Font stack** (verbatim, from `THEME.font_stack`): `"Fragment Mono", "DM Mono", "Fira Code", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`.
- **Icon provider locked:** icoziv only (`https://i.icoziv.workers.dev/icons?i=...&cr=3`). No new providers.
- **No fake data:** every rendered number must come from `fetch_profile()` or the GitHub REST events API. No invented metrics, no static "levels" or "stats".
- **Fallback never fails the build:** any generator network failure renders a graceful fallback (zeros / "no activity yet") instead of raising.
- **Calendar-based visualizations exactly 2** (heatmap + Pac-Man); no other contribution renders may remain.
- **CLI/test conventions:** run tests with `python -m pytest scripts/tests/ -v` from repo root; syntax-check with `python -m py_compile <file>` (ruff not installed locally). Each new test file must start with the sys.path shim (see Task 1). `scripts/conftest.py` already adds `scripts/` to `sys.path`.
- **Git:** always `GIT_EDITOR=true git pull --rebase origin main` before pushing (bare pull opens nvim and hangs the shell); the orchestrator auto-commits assets daily, so expect push rejections.
- **No code comments** unless they document a non-obvious constraint (existing files do this sparingly).

---

### Task 1: Achievements module (pure rules)

**Files:**

- Create: `scripts/core/achievements.py`
- Create: `scripts/tests/test_achievements.py`

**Interfaces:**

- Consumes: nothing (pure function over a `profile` dict shaped like `core.github._parse_profile` output — keys `name, login, commits, merged_prs, reviews, closed_issues, repos, stars, followers, current_streak, longest_streak, languages, primary_language, years`).
- Produces: `ACHIEVEMENTS: list[dict]` (7 entries, each `{"id", "emoji", "name"}`) and `compute_achievements(profile: dict) -> list[dict]` where each returned dict is an `ACHIEVEMENTS` entry plus an `"earned": bool` key. Task 2 consumes this.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Tests for achievement rules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.achievements import ACHIEVEMENTS, compute_achievements


def _make_profile(**overrides) -> dict:
    base = {
        "name": "Test User",
        "login": "testuser",
        "commits": 0,
        "merged_prs": 0,
        "reviews": 0,
        "closed_issues": 0,
        "repos": 0,
        "stars": 0,
        "followers": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "languages": [],
        "primary_language": "Unknown",
        "years": 0,
    }
    base.update(overrides)
    return base


def _earned_ids(profile: dict) -> set[str]:
    return {a["id"] for a in compute_achievements(profile) if a["earned"]}


class TestAchievementRules:
    def test_all_earned_when_thresholds_met(self):
        profile = _make_profile(
            merged_prs=50,
            longest_streak=30,
            current_streak=14,
            stars=100,
            repos=5,
            languages=[{"name": "HCL", "bytes": 1}, {"name": "Go", "bytes": 1}],
            years=2,
        )
        assert _earned_ids(profile) == {
            "ship_it", "streak_lord", "night_owl",
            "star_surfer", "builder", "cloud_arch", "veteran",
        }

    def test_none_earned_on_zero_profile(self):
        assert _earned_ids(_make_profile()) == set()

    def test_empty_profile_no_crash(self):
        assert _earned_ids({}) == set()

    def test_boundary_ship_it(self):
        assert "ship_it" in _earned_ids(_make_profile(merged_prs=50))
        assert "ship_it" not in _earned_ids(_make_profile(merged_prs=49))

    def test_boundary_streak_lord(self):
        assert "streak_lord" in _earned_ids(_make_profile(longest_streak=30))
        assert "streak_lord" not in _earned_ids(_make_profile(longest_streak=29))

    def test_boundary_night_owl(self):
        assert "night_owl" in _earned_ids(_make_profile(current_streak=14))
        assert "night_owl" not in _earned_ids(_make_profile(current_streak=13))

    def test_boundary_star_surfer(self):
        assert "star_surfer" in _earned_ids(_make_profile(stars=100))
        assert "star_surfer" not in _earned_ids(_make_profile(stars=99))

    def test_boundary_builder(self):
        assert "builder" in _earned_ids(_make_profile(repos=5))
        assert "builder" not in _earned_ids(_make_profile(repos=4))

    def test_boundary_veteran(self):
        assert "veteran" in _earned_ids(_make_profile(years=2))
        assert "veteran" not in _earned_ids(_make_profile(years=1.9))

    def test_cloud_arch_needs_two_cloud_langs(self):
        two = _make_profile(languages=[{"name": "HCL", "bytes": 1}, {"name": "YAML", "bytes": 1}])
        one = _make_profile(languages=[{"name": "HCL", "bytes": 1}])
        none = _make_profile(languages=[{"name": "Python", "bytes": 1}])
        assert "cloud_arch" in _earned_ids(two)
        assert "cloud_arch" not in _earned_ids(one)
        assert "cloud_arch" not in _earned_ids(none)


class TestAchievementShape:
    def test_has_expected_fields(self):
        for a in compute_achievements(_make_profile()):
            assert set(a.keys()) == {"id", "emoji", "name", "earned"}
            assert isinstance(a["earned"], bool)

    def test_order_matches_constant(self):
        computed = compute_achievements(_make_profile())
        assert [c["id"] for c in computed] == [a["id"] for a in ACHIEVEMENTS]
        assert len(computed) == 7
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest scripts/tests/test_achievements.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.achievements'`

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest scripts/tests/test_achievements.py -v`
Expected: PASS, 12 tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/core/achievements.py scripts/tests/test_achievements.py
git commit -m "feat: add achievement rules (pure functions)"
```

---

### Task 2: Fused profile header generator

**Files:**

- Create: `scripts/generators/header.py`
- Create: `scripts/tests/test_header.py`

**Interfaces:**

- Consumes: `core.github.fetch_profile(token)` → profile dict; `generators.rpg_card.compute_character(profile)` → char dict (keys incl. `name, class_name, class_desc, level, rarity, rarity_color, commits, current_streak, primary_language, languages, login`); `core.achievements.compute_achievements(profile)` → `list[dict]`; `core.svg.svg_header/background_rect/escape`; `core.theme.THEME`.
- Produces: `build_header(profile: dict) -> str` (pure, returns full SVG string) and `render(output_path="assets/profile-header.svg", profile=None, token=None) -> None` (fetches profile when `profile` is None, writes SVG). Task 4's cli.py calls `render_header()`; Task 6's README references `assets/profile-header.svg`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Tests for the fused profile header generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.github import _fallback_profile
from generators.header import build_header, render


def _make_profile(**overrides) -> dict:
    base = {
        "name": "Mahesh Diwan",
        "login": "mahesh-diwan",
        "commits": 1284,
        "merged_prs": 96,
        "reviews": 12,
        "closed_issues": 30,
        "repos": 15,
        "stars": 50,
        "followers": 150,
        "current_streak": 14,
        "longest_streak": 40,
        "languages": [
            {"name": "Python", "bytes": 5000},
            {"name": "Bash", "bytes": 3000},
            {"name": "Go", "bytes": 2000},
        ],
        "primary_language": "Python",
        "years": 3.0,
    }
    base.update(overrides)
    return base


class TestBuildHeader:
    def test_returns_svg(self):
        svg = build_header(_make_profile())
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")

    def test_contains_name_and_class(self):
        svg = build_header(_make_profile())
        assert "Mahesh Diwan" in svg
        assert "Automancer" in svg

    def test_contains_stat_chips(self):
        svg = build_header(_make_profile())
        assert "LVL" in svg
        assert "COMMITS" in svg
        assert "STREAK" in svg
        assert "1,284" in svg

    def test_smil_only_no_css_no_import(self):
        svg = build_header(_make_profile())
        assert "@keyframes" not in svg
        assert "@import" not in svg
        assert "fonts.googleapis.com" not in svg
        assert "<animate" in svg

    def test_earned_and_locked_pills(self):
        svg = build_header(_make_profile())
        assert 'fill="#00D4FF" opacity="0.15"' in svg      # earned pill (cyan fill)
        assert 'stroke="#8b949e" stroke-dasharray="4 3"' in svg  # locked pill (dashed)

    def test_name_escaped(self):
        svg = build_header(_make_profile(name="A & B"))
        assert "A &amp; B" in svg

    def test_fallback_profile_renders(self):
        """A zeroed profile (what render() gets when GraphQL fails) must not crash."""
        svg = build_header(_fallback_profile())
        assert svg.startswith("<svg")
        assert "LVL" in svg


class TestRender:
    def test_writes_file(self, tmp_path):
        out = tmp_path / "profile-header.svg"
        render(str(out), profile=_make_profile())
        assert out.read_text().startswith("<svg")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest scripts/tests/test_header.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'generators.header'`

- [ ] **Step 3: Write minimal implementation**

```python
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
    parts = [f'<rect x="{x}" y="{y}" width="72" height="72" rx="8" fill="{THEME.surface}"/>']
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
        f'<text x="104" y="62" fill="{char['rarity_color']}" font-size="13" font-weight="bold">'
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest scripts/tests/test_header.py -v`
Expected: PASS, 8 tests.

- [ ] **Step 5: Syntax-check the new file**

Run: `python -m py_compile scripts/generators/header.py`
Expected: exit 0, no output.

- [ ] **Step 6: Commit**

```bash
git add scripts/generators/header.py scripts/tests/test_header.py
git commit -m "feat: add fused profile header generator (SMIL, no external imports)"
```

---

### Task 3: Recent activity generator

**Files:**

- Create: `scripts/generators/activity.py`
- Create: `scripts/tests/test_activity.py`

**Interfaces:**

- Consumes: `core.github.USERNAME` (="mahesh-diwan") and `core.github._retry_get(url, retries, delay, **kwargs)`; `core.svg.svg_header/background_rect/title_bar/escape`; `core.theme.THEME`.
- Produces: `_parse_events(events: list[dict], limit: int = 5) -> list[str]` (filters to PushEvent/PullRequestEvent/IssueCommentEvent/ReleaseEvent, formats terminal-log lines, returns fallback line when empty), `build_svg(lines: list[str]) -> str` (pure), and `render(output_path="assets/recent-activity.svg", token=None) -> None`. Task 4's cli.py calls `render_activity()`; Task 6's README references `assets/recent-activity.svg`.

- [ ] **Step 1: Write the failing test**

```python
#!/usr/bin/env python3
"""Tests for the recent-activity generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.activity import FALLBACK_LINE, _parse_events, build_svg


def _event(etype: str, **payload) -> dict:
    ev = {"type": etype, "repo": {"name": "mahesh-diwan/flexfetch"}, "payload": {}}
    ev["payload"].update(payload)
    return ev


def _pr_event(action: str, number: int) -> dict:
    ev = _event("PullRequestEvent")
    ev["payload"] = {"action": action, "pull_request": {"number": number}}
    return ev


class TestParseEvents:
    def test_push_multiple_commits(self):
        events = [_event("PushEvent", size=3, commits=[{}, {}, {}])]
        assert _parse_events(events) == ["- pushed 3 commits → flexfetch"]

    def test_push_single_commit_singular(self):
        events = [_event("PushEvent", size=1, commits=[{}])]
        assert _parse_events(events) == ["- pushed 1 commit → flexfetch"]

    def test_pr_opened(self):
        assert _parse_events([_pr_event("opened", 12)]) == ["- opened PR #12 → flexfetch"]

    def test_pr_merged(self):
        assert _parse_events([_pr_event("merged", 12)]) == ["- merged PR #12 → flexfetch"]

    def test_issue_comment(self):
        ev = _event("IssueCommentEvent", action="created", issue={"number": 5})
        assert _parse_events([ev]) == ["- commented on #5 → flexfetch"]

    def test_release(self):
        ev = _event("ReleaseEvent", action="published", release={"tag_name": "v0.3.1"})
        assert _parse_events([ev]) == ["- released v0.3.1 → flexfetch"]

    def test_ignores_other_event_types(self):
        star = _event("StarEvent", action="created", starred_at="x")
        fork = _event("ForkEvent", forkee={"id": 1})
        assert _parse_events([star, fork]) == [FALLBACK_LINE]

    def test_limit_applies(self):
        events = [_event("PushEvent", size=2, commits=[{}, {}]) for _ in range(10)]
        lines = _parse_events(events)
        assert len(lines) == 5

    def test_malformed_event_no_crash(self):
        assert _parse_events([{}]) == [FALLBACK_LINE]
        assert _parse_events([{"type": "PushEvent"}]) == ["- pushed 1 commit → unknown"]

    def test_empty_returns_fallback(self):
        assert _parse_events([]) == [FALLBACK_LINE]


class TestBuildSvg:
    def test_contains_prompt_and_lines(self):
        svg = build_svg(["- pushed 3 commits → flexfetch"])
        assert "tail -f ~/.github.log" in svg
        assert "pushed 3 commits" in svg
        assert svg.startswith("<svg") and svg.endswith("</svg>")

    def test_escapes_special_chars(self):
        svg = build_svg(["- released v1.0 & <beta>"])
        assert "&amp;" in svg
        assert "&lt;" in svg

    def test_smil_only(self):
        svg = build_svg([FALLBACK_LINE])
        assert "<animate" in svg
        assert "@keyframes" not in svg
        assert "@import" not in svg
        assert "fonts.googleapis.com" not in svg
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest scripts/tests/test_activity.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'generators.activity'`

- [ ] **Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Generate a recent-activity log SVG from public GitHub events.

Shows up to 5 recent Push / PR / IssueComment / Release events as terminal
log lines. Renders a graceful fallback line when the API is unavailable.
"""

import os
from pathlib import Path

from core.github import USERNAME, _retry_get
from core.svg import background_rect, escape, svg_header, title_bar
from core.theme import THEME

EVENT_TYPES = {"PushEvent", "PullRequestEvent", "IssueCommentEvent", "ReleaseEvent"}
FALLBACK_LINE = "- no activity yet — go ship something"


def _repo_name(event: dict) -> str:
    name = (event.get("repo") or {}).get("name") or ""
    return name.split("/")[-1] if name else "unknown"


def _format_event(event: dict) -> str | None:
    etype = event.get("type")
    if etype not in EVENT_TYPES:
        return None
    repo = _repo_name(event)
    payload = event.get("payload") or {}
    if etype == "PushEvent":
        n = payload.get("size") or len(payload.get("commits") or []) or 1
        unit = "commit" if n == 1 else "commits"
        return f"- pushed {n} {unit} → {repo}"
    if etype == "PullRequestEvent":
        num = (payload.get("pull_request") or {}).get("number")
        verb = {
            "opened": "opened PR",
            "merged": "merged PR",
            "closed": "closed PR",
            "reopened": "reopened PR",
        }.get(payload.get("action") or "", "PR")
        return f"- {verb} #{num} → {repo}" if num is not None else f"- {verb} → {repo}"
    if etype == "IssueCommentEvent":
        num = (payload.get("issue") or {}).get("number")
        return f"- commented on #{num} → {repo}" if num is not None else f"- commented → {repo}"
    if etype == "ReleaseEvent":
        tag = (payload.get("release") or {}).get("tag_name") or "release"
        return f"- released {tag} → {repo}"
    return None


def _parse_events(events: list[dict], limit: int = 5) -> list[str]:
    """Pick the first `limit` formattable events and render as log lines."""
    lines: list[str] = []
    for event in events:
        line = _format_event(event)
        if line:
            lines.append(line)
        if len(lines) >= limit:
            break
    return lines or [FALLBACK_LINE]


def build_svg(lines: list[str]) -> str:
    """Build the activity log SVG (pure — no I/O)."""
    width = 760
    height = 32 + len(lines) * 24 + 20
    parts = [
        svg_header(width, height),
        background_rect(width, height),
        title_bar(width, "mahesh@github ~ $ tail -f ~/.github.log"),
    ]
    for i, line in enumerate(lines):
        parts.append(
            f'<text x="20" y="{56 + i * 24}" fill="{THEME.muted}" font-size="12">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" '
            f'begin="{0.2 + i * 0.2}s" fill="freeze"/>'
            f"{escape(line)}</text>"
        )
    parts.append("</svg>")
    return "\n".join(parts)


def render(output_path: str = "assets/recent-activity.svg", token: str | None = None) -> None:
    """Fetch recent public events and write the activity log SVG."""
    token = token or os.environ.get("GITHUB_TOKEN", "")
    headers = {"Authorization": f"bearer {token}"} if token else {}
    try:
        resp = _retry_get(
            f"https://api.github.com/users/{USERNAME}/events/public",
            params={"per_page": "20"},
            headers=headers,
        )
        lines = _parse_events(resp.json())
    except Exception as e:
        print(f"Activity fetch failed: {e}")
        lines = [FALLBACK_LINE]
    svg = build_svg(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(svg)
    print(f"Wrote {output_path} — {len(lines)} event lines")


if __name__ == "__main__":
    render()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest scripts/tests/test_activity.py -v`
Expected: PASS, 13 tests.

- [ ] **Step 5: Commit**

```bash
git add scripts/generators/activity.py scripts/tests/test_activity.py
git commit -m "feat: add recent-activity log generator (SMIL, graceful fallback)"
```

---

### Task 4: Wire cli.py, delete orphaned generators + dead assets

**Files:**

- Modify: `scripts/cli.py`
- Delete: `scripts/generators/ascii.py`, `scripts/generators/infocard.py`
- Delete: `assets/breakout.svg`, `assets/breakout-dark.svg`, `assets/mahesh-ascii.svg`, `assets/info-card.svg`

**Interfaces:**

- Consumes: Task 2 `generators.header.render`, Task 3 `generators.activity.render`, existing `generators.heatmap.render(data)`, `generators.rpg_card.render()`.
- Produces: `python -m scripts build` generates heatmap + rpg_card + header + activity. Task 5's workflow and Task 6's README depend on the `header`/`activity` targets existing.

- [ ] **Step 1: Rewrite `scripts/cli.py`**

Replace the whole file with:

```python
#!/usr/bin/env python3
"""Unified CLI entrypoint for all profile art generators.

Usage:
    python -m scripts build               # Generate all assets
    python -m scripts build heatmap       # Generate one asset
    python -m scripts fetch               # Fetch contribution data only
    python -m scripts test                # Run tests
"""

import argparse
import sys
from pathlib import Path

# Ensure scripts/ is on path for relative imports
sys.path.insert(0, str(Path(__file__).parent))


def cmd_build(args):
    """Generate all assets (or a specific one)."""
    from core.github import fetch
    from generators.activity import render as render_activity
    from generators.header import render as render_header
    from generators.heatmap import render as render_heatmap
    from generators.rpg_card import render as render_rpg

    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    target = args.target if hasattr(args, "target") else None

    if target in (None, "heatmap"):
        data = fetch()
        render_heatmap(data)
    if target in (None, "rpg_card"):
        render_rpg()
    if target in (None, "header"):
        render_header()
    if target in (None, "activity"):
        render_activity()


def cmd_fetch(args):
    """Fetch contribution data only."""
    from core.github import fetch

    fetch()


def cmd_test(args):
    """Run tests."""
    import pytest

    sys.exit(pytest.main(["-v", "scripts/"]))


def main():
    parser = argparse.ArgumentParser(description="Profile art generator")
    sub = parser.add_subparsers(dest="command")

    build_p = sub.add_parser("build", help="Generate assets")
    build_p.add_argument(
        "target", nargs="?", choices=["heatmap", "rpg_card", "header", "activity"]
    )

    sub.add_parser("fetch", help="Fetch contribution data")
    sub.add_parser("test", help="Run tests")

    args = parser.parse_args()

    if args.command == "build":
        cmd_build(args)
    elif args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "test":
        cmd_test(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Delete orphaned generators and dead assets**

Run:

```bash
git rm scripts/generators/ascii.py scripts/generators/infocard.py
git rm assets/breakout.svg assets/breakout-dark.svg assets/mahesh-ascii.svg assets/info-card.svg
```

- [ ] **Step 3: Verify no remaining references**

Run: `grep -rn "ascii\|infocard\|breakout" scripts/ --include="*.py" | grep -v "test_" ; grep -rn "ascii\|infocard" README.md || true`
Expected: no output for the first grep (no code references). The README grep may match lines the Task 6 rewrite removes — Task 6 will fix.

- [ ] **Step 4: Verify full test suite + build**

Run:

```bash
python -m pytest scripts/tests/ -v
PYTHONPATH=scripts python -m scripts build
```

Expected: all tests PASS (existing 34 + 12 achievements + 8 header + 13 activity = 67). Build writes `assets/contrib-heatmap.svg`, `assets/rpg-card.svg`, `assets/profile-header.svg`, `assets/recent-activity.svg` without error (heatmap/RPG use network; fallbacks keep them from raising).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: wire header+activity into cli, drop ascii/infocard generators and dead assets"
```

---

### Task 5: Workflow — drop breakout, keep pacman

**Files:**

- Modify: `.github/workflows/profile-orchestrator.yml`

**Interfaces:**

- Consumes: Task 4's `python -m scripts build` (now includes header + activity).
- Produces: generates `assets/pacman.svg`/`assets/pacman-dark.svg` only; assets hash + deploy unchanged.

- [ ] **Step 1: Edit the Pac-Man action input**

In `.github/workflows/profile-orchestrator.yml`, change line 50 from:

```yaml
games: "pacman,breakout"
```

to:

```yaml
games: "pacman"
```

- [ ] **Step 2: Delete the breakout copy steps**

In `.github/workflows/profile-orchestrator.yml`, delete lines 57-58:

```yaml
cp dist/breakout-contribution-graph.svg assets/breakout.svg 2>/dev/null || true
cp dist/breakout-contribution-graph-dark.svg assets/breakout-dark.svg 2>/dev/null || true
```

The remaining copy step block should be exactly:

```yaml
- name: Copy Pac-Man SVGs to assets
  run: |
    cp dist/pacman-contribution-graph.svg assets/pacman.svg 2>/dev/null || true
    cp dist/pacman-contribution-graph-dark.svg assets/pacman-dark.svg 2>/dev/null || true
```

- [ ] **Step 3: Validate workflow YAML**

Run: `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/profile-orchestrator.yml')); print('ok')"` (PyYAML may not be installed locally — if it is not, skip this check and rely on the GitHub YAML parser at next workflow run).
Expected: `ok` (or skip).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/profile-orchestrator.yml
git commit -m "chore: drop breakout from profile orchestrator"
```

---

### Task 6: Restructure README to locked layout

**Files:**

- Modify: `README.md` (full rewrite)

**Interfaces:**

- Consumes: all asset files produced by Tasks 2-5 — `assets/profile-header.svg`, `assets/recent-activity.svg`, `assets/pacman.svg`, `assets/pacman-dark.svg`, existing `assets/contrib-heatmap.svg`.
- Produces: the final profile page per the locked A3 layout.

- [ ] **Step 1: Rewrite `README.md`**

Replace the entire file with:

```markdown
<div align="center">

# **Mahesh Diwan**

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:00D4FF,100:0d1117&height=200&section=header&text=Mahesh%20Diwan&fontSize=36&fontColor=00D4FF&fontAlignY=35&desc=DevOps%20Engineer%20%7C%20Cloud%20%7C%20CI/CD&descSize=16&descAlignY=55&animation=fadeIn" width="100%" alt="Animated header banner" />

</div>

### ✓ status: currently refactoring flexfetch

[![Profile CI](https://github.com/mahesh-diwan/mahesh-diwan/actions/workflows/profile-orchestrator.yml/badge.svg)](https://github.com/mahesh-diwan/mahesh-diwan/actions)

<img src="./assets/profile-header.svg" width="760" alt="Mahesh Diwan — profile header" />

<div align="center">

<img src="./assets/contrib-heatmap.svg" width="860" alt="GitHub contribution heatmap — auto-refreshed daily" />

</div>

---

### `mahesh@github ~ $ ./arcade.sh`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/pacman-dark.svg" />
  <img alt="GitHub Contribution Pac-Man" src="./assets/pacman.svg" />
</picture>

---

### `mahesh@github ~ $ cat ~/.ssh/authorized_keys`

<p align="center">
  <a href="https://linkedin.com/in/mahesh-diwan"><img src="https://i.icoziv.workers.dev/icons?i=linkedin&cr=3" width="32" alt="LinkedIn" /></a>
  &nbsp;&nbsp;
  <a href="https://github.com/mahesh-diwan"><img src="https://i.icoziv.workers.dev/icons?i=github&cr=3" width="32" alt="GitHub" /></a>
  &nbsp;&nbsp;
  <a href="https://x.com/mahesh_diwan1/"><img src="https://i.icoziv.workers.dev/icons?i=twitter&cr=3" width="32" alt="X / Twitter" /></a>
  &nbsp;&nbsp;
  <a href="https://www.instagram.com/mahesh_diwan1"><img src="https://i.icoziv.workers.dev/icons?i=instagram&cr=3" width="32" alt="Instagram" /></a>
  &nbsp;&nbsp;
  <a href="https://mahesh1215.hashnode.dev/"><img src="https://i.icoziv.workers.dev/icons?i=hashnode&cr=3" width="32" alt="Blog" /></a>
  &nbsp;&nbsp;
  <img src="https://i.icoziv.workers.dev/icons?i=aws,terraform,docker,kubernetes,jenkins,githubactions,python,bash,go,prometheus,grafana,nginx,ansible,git,linux,ubuntu&perline=16&cr=3" alt="Tech stack" />
</p>

---

<details>
<summary><strong>📜 Recent activity</strong></summary>

<img src="./assets/recent-activity.svg" width="760" alt="Recent GitHub activity" />

</details>

<details>
<summary><strong>📦 Featured projects</strong></summary>

| Project                                                                          | Description                                                                       |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [**flexfetch**](https://github.com/mahesh-diwan/flexfetch)                       | System info tool — Lua plugins, Tera templates, 5 themes, parallel detection      |
| [**a11y-forge**](https://github.com/mahesh-diwan/a11y-forge)                     | WCAG 2.2 AA accessibility scanner with AI grouping and PDF reports                |
| [**recap**](https://github.com/mahesh-diwan/recap)                               | Local AI (Ollama) YouTube summarizer — chapters, timestamps, Markdown export      |
| [**DeskTap**](https://github.com/mahesh-diwan/DeskTap)                           | Desk-tap detection via microphone, 4-zone ML classification, configurable actions |
| [**AWS-Resource-Tracker**](https://github.com/mahesh-diwan/AWS-Resource-Tracker) | Bash script that reports AWS resource usage stats via the CLI                     |

</details>

<details>
<summary><strong>✍️ Blog posts</strong></summary>

| Post                                                                                                                                                              | Date |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| [AWS Resource Tracking](https://mahesh1215.hashnode.dev/automate-aws-resource-tracking-with-ease)                                                                 | 2024 |
| [Deploy Node.js on EC2](https://mahesh1215.hashnode.dev/from-github-to-aws-deploy-your-first-nodejs-app-on-ec2)                                                   | 2024 |
| [CI/CD with Jenkins, SonarQube, Docker](https://mahesh1215.hashnode.dev/a-beginners-guide-to-setting-up-a-cicd-pipeline-with-jenkins-sonarqube-and-docker-on-aws) | 2024 |
| [Docker Deployments with Jenkins & Ansible](https://mahesh1215.hashnode.dev/beginners-guide-automating-docker-deployments-with-jenkins-ansible-and-github)        | 2024 |

> ✍️ **Full blog:** [mahesh1215.hashnode.dev](https://mahesh1215.hashnode.dev/)

</details>

---

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=DM+Mono&weight=500&size=20&duration=2000&pause=1000&color=00D4FF&center=true&vCenter=true&width=500&height=45&lines=Thanks+for+visiting!+%F0%9F%91%8B;Have+a+great+day!+%E2%9C%A8" alt="Thanks" />

**📫 Open to opportunities** — DevOps, Platform Engineering, Cloud Infrastructure

<a href="https://github.com/mahesh-diwan">
<img src="https://komarev.com/ghpvc/?username=mahesh-diwan&label=PROFILE%20VIEWS&color=00D4FF&style=flat-square&labelColor=161b22" alt="Profile views" />
</a>

</div>

---

### 🤖 For agents

This profile is **agent-readable**. If you're an LLM or agent, read
[`AGENTS.md`](./AGENTS.md) for structured facts and citation guidance, or
[`llms.txt`](./llms.txt) for a terse machine-parseable summary.
```

Note on decisions taken here:

- Top typing SVG and the `whoami`/RPG/streak/activity-graph/breakout sections are gone per the locked layout; the small footer "Thanks for visiting" typing SVG is kept as the one playful flourish.
- The "For agents" block moved to the footer (it is for machines, not page readers) — it is not removed.
- Status strip text `currently refactoring flexfetch` is a human-edited placeholder, per spec §3.4.

- [ ] **Step 2: Verify no dead references remain**

Run: `grep -n "breakout\|activity-graph\|streak-stats\|mahesh-ascii\|info-card\|rpg-card" README.md || true`
Expected: no matches.

- [ ] **Step 3: Verify all embedded assets exist**

Run: `for f in assets/profile-header.svg assets/recent-activity.svg assets/pacman.svg assets/pacman-dark.svg assets/contrib-heatmap.svg; do test -f "$f" || echo "MISSING $f"; done`
Expected: no output (all present; `profile-header.svg` + `recent-activity.svg` created by Task 4's build step).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: restructure README to A3 stats-board layout"
```

---

## Post-plan verification (run after Task 6)

Run: `python -m pytest scripts/tests/ -v` → expect 67 passing.
Run: `git status --short` → expect clean.
Push sequence (from repo root): `git push` — if rejected (orchestrator auto-commit), run `GIT_EDITOR=true git pull --rebase origin main && git push`.

After push, verify against the acceptance criteria:

1. Calendar visualizations exactly 2 (heatmap + Pac-Man); confirm `README.md` contains no `breakout`, `activity-graph`, or `streak-stats` references.
2. Fused header + achievements + status strip + recent activity all render (`assets/profile-header.svg` + `assets/recent-activity.svg` exist and contain `<svg`).
3. Playwright audit: reload `github.com/mahesh-diwan`, assert every profile `<img>` has `naturalWidth > 0` and 0 console errors.
4. Orchestrator workflow green on next scheduled/dispatch run (Games input now `pacman` only).

## Self-Review (writing-plans checklist)

**1. Spec coverage** — walked every spec section: §3.1 achievements → Task 1; §3.2 header → Task 2; §3.3 activity → Task 3; §3.4 status strip → Task 6 README; §4.1 cli → Task 4; §4.2 workflow → Task 5; §4.3 README → Task 6; §4.4 deletions → Tasks 4 + 5; §5 tests → Tasks 1-3 (test files) + Task 4 full-suite run; §7 acceptance → post-plan verification block. No gaps.

**2. Placeholder scan** — no TBD/TODO; every code step contains full file content or exact line-level edits; no "add error handling" prose without code.

**3. Type consistency** — `compute_achievements` returns `list[dict]` with `{id,emoji,name,earned}` and Task 2 consumes exactly those keys; `compute_character` keys used in `build_header` (`name,class_name,rarity,rarity_color,commits,streak,primary_language,languages,class_desc,level`) all match `rpg_card.py:114-135` output; `_parse_events`/`build_svg`/`render` names consistent across Task 3 and cli wiring (`render_activity`, `render_header`); cli choices list matches the four `render_*` branches.

Known implementation detail worth flagging to the executor: Task 2's `test_fallback_profile_renders` exercises the real degraded path — when `fetch_profile()` has no token it returns `core.github._fallback_profile()` (all keys zeroed), which `build_header` renders without raising. No change to `rpg_card.py` is required.
