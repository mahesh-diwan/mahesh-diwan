# 2026-08-06 Profile Redesign — Design Spec

**Goal:** Remove redundancy + clutter from the GitHub profile README. Deliver
one cohesive "stats board" with a fused profile header, one contribution
visualization (heatmap) + one game (Pac-Man), and 3 new auto-computed
features (achievements, status strip, recent activity).

## 1. Problem

Current profile renders the same contribution calendar 4 times (heatmap,
activity graph, Pac-Man, Breakout), plus overlapping stat blocks (RPG card
stats, streak card) = 5-6 duplicated stat areas stacked vertically. Each
carries its own identical-looking terminal heading → cluttered, repetitive.

## 2. Approved design (locked with user)

Top-to-bottom page flow:

```
┌──────────────────────────────────────────────┐
│  capsule banner  (name + tagline, animated)   │
├──────────────────────────────────────────────┤
│  ✓ status: currently <what> · [CI badge]     │  ← NEW status strip (human-maintained)
├──────────────────────────────────────────────┤
│  ┌─ fused profile header ─────────────────┐  │  ← NEW profile-header.svg
│  │ ▚▞ avatar  Automancer · Epic           │  │
│  │           Python / Bash / Go —         │  │
│  │           automates cloud pipelines    │  │
│  │ 🏆 ⚡ 🔥 ☁️ achievement pills           │  │  ← NEW achievements
│  │ LVL 24 · COMMITS 1,284 · STREAK 14     │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌─ heatmap (full width) ─────────────────┐  │
│  └────────────────────────────────────────┘  │
├──────────────────────────────────────────────┤
│  ./arcade.sh                                │
│  ┌─ pacman.svg (dark/light) ──────────────┐  │  ← only game (breakout dropped)
│  └────────────────────────────────────────┘  │
├──────────────────────────────────────────────┤
│  socials + toolbox (one compact icoziv row)  │
├──────────────────────────────────────────────┤
│  ▸ <details> recent activity  ← NEW activity.svg (5 real events)
│  ▸ <details> projects & blog  (existing tables)
├──────────────────────────────────────────────┤
│  thanks for visiting · open to opportunities │
└──────────────────────────────────────────────┘
```

### 2.1 Removed (kill the redundancy)

- `assets/breakout.svg`, `assets/breakout-dark.svg` + README breakout section
- github-readme-activity-graph (activity graph — dup heatmap)
- github-readme-streak-stats card (streak stats — dup of RPG card + chips)
- `assets/mahesh-ascii.svg` + `assets/info-card.svg` + their `whoami` table
  (replaced by the fused header)
- Orphaned generators `ascii.py`, `infocard.py`

### 2.2 Kept

- capsule banner, heatmap (`contrib-heatmap.svg`), Pac-Man
  (`pacman.svg`/`pacman-dark.svg` via `<picture>`), CI badge, komarev counter,
  icoziv social + tech icons, `<details>` projects + blog tables, footer.

## 3. New components

### 3.1 `scripts/core/achievements.py` (NEW)

Pure functions, no I/O:

- `compute_achievements(profile: dict) -> list[dict]`
  each `{ "id", "emoji", "name", "earned" }`. All rules data-backed from
  `fetch_profile()` output — no invented metrics.
- Rules:
  - `ship_it` 🚢 Ship It — merged_prs >= 50
  - `streak_lord` 🔥 Streak Lord — longest_streak >= 30
  - `night_owl` 🦉 Night Owl — current_streak >= 14
  - `star_surfer` ⭐ Star Surfer — stars >= 100
  - `builder` 🧱 Builder — repos >= 5
  - `cloud_arch` ☁️ Multi-cloud — language set ∩ {HCL, YAML, Dockerfile, Go, Bash} >= 2
  - `veteran` ⏳ Veteran — years >= 2
- Unearned achievements render dimmed (visible-but-locked = aspirational).

### 3.2 `scripts/generators/header.py` (NEW)

- `render(output_path="assets/profile-header.svg")`
- Data: `fetch_profile()` + `compute_character()` + `compute_achievements()`.
- SVG (~760×170): compact block-art avatar tile (drawn with `▚▞` blocks, NOT
  the full portrait), name, `Class · Rarity`, tagline, achievement pills
  (earned = cyan fill, locked = muted outline), 3 stat chips
  (LVL / COMMITS / STREAK).
- Uses `core.svg` helpers + `core.theme` tokens; SMIL-only animation
  (fade-slide stagger via `<animate>`) — no CSS keyframes, no @import
  (GitHub `<img>` renderer blocks external resources — hard requirement).
- Fallback: `_fallback_profile()` already returns zeros → renders an empty
  header rather than failing.

### 3.3 `scripts/generators/activity.py` (NEW)

- `render(output_path="assets/recent-activity.svg")`
- Data: GitHub REST `GET /users/{login}/events/public?per_page=20`, pick first
  5 PushEvent / PullRequestEvent / IssueCommentEvent / ReleaseEvent, format as
  terminal log lines (`mahesh@github ~ $ tail -f ~/.github.log`):
  `- pushed 3 commits → flexfetch` / `- opened PR #12 → a11y-forge`
  / `- released recap v0.3.1`.
- Uses `core.github._retry_get` (respects rate limits, falls back gracefully).
- SMIL stagger reveal. On no token / API failure → renders
  `- no activity yet — go ship something` line (never fails the build).

### 3.4 Status strip (README-only, no generator)

Single markdown line under the banner, human-maintained:

```
### ✓ status: currently refactoring flexfetch · [![CI badge]]
```

The "currently X" text is manually edited (a workflow cannot know intent);
the CI badge is the live "last build passing" signal. Lazy by design.

## 4. Changes to existing files

### 4.1 `scripts/cli.py`

- Add `header`, `activity` to build targets + choices list; wire imports.

### 4.2 `.github/workflows/profile-orchestrator.yml`

- Pac-Man action: `games: "pacman"` (drop breakout).
- Delete breakout copy steps (lines 57-58).
- `python -m scripts build` already covers new generators once wired in cli.

### 4.3 `README.md`

Restructure to the locked layout (Section 2). Delete breakout section,
activity graph, streak card, whoami table. Add status strip, profile-header.svg
in place of whoami, recent-activity.svg inside `<details>`.

### 4.4 Deletions

- `assets/breakout.svg`, `assets/breakout-dark.svg`,
  `assets/mahesh-ascii.svg`, `assets/info-card.svg`
- `scripts/generators/ascii.py`, `scripts/generators/infocard.py`

## 5. Testing

- `scripts/tests/test_achievements.py` (NEW): each rule fires with
  satisfying profile, stays off below threshold, empty profile → all unearned.
- `scripts/tests/test_header.py` (NEW): SVG renders, contains name + chips;
  `compute_character` + `compute_achievements` compose without error.
- `scripts/tests/test_activity.py` (NEW): event parsing (sample JSON), empty
  events → fallback line, malformed payload → fallback line.
- Existing 34 tests keep passing (some may need fixture updates if they import
  deleted generators).

## 6. Non-goals / out of scope

- No real click-to-play games (impossible in `<img>`; SMIL only).
- No Vercel/serverless endpoints.
- No new icon providers (icoziv only, stays).
- No theme change (palette locked: #0d1117 / #161b22 / #21262d / #00D4FF).

## 7. Acceptance criteria

- Calendar-based visualizations exactly 2 (heatmap + Pac-Man); no other
  contribution renders remain (activity graph, streak card, breakout gone).
- Fused header, achievements, status strip, recent activity all render.
- Zero broken `<img>` (Playwright audit: all naturalWidth > 0, 0 console errors).
- 34+ tests green; orchestrator workflow green.
