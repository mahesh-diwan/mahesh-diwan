# GitHub README Redesign — Execution Plan

Source: Research of 10 exemplary GitHub profiles + audit of mahesh-diwan profile

## Phase 1: Fun & Creative (NEW)

### 1A. RPG Character Card (GitHub Action)

**What:** A daily-generated SVG card that turns your GitHub activity into an RPG character sheet. Your primary language (Python) maps to a class. Commits = XP, PRs = quests, issues = bounties. Rarity tiers: Common → Rare → Epic → Legendary → Mythic.

**How:** Python script (`scripts/generators/rpg_card.py`) runs in the orchestrator workflow. Fetches GitHub data via GraphQL, computes XP/level/class/rarity, generates SVG card with #0d1117/#00D4FF palette.

**Based on:** GitLevel (GavinnnTann/GitLevel) — MIT licensed, zero deps, well-structured XP formula.

**Stats used:**

| Stat          | Source                                | Weight             |
| ------------- | ------------------------------------- | ------------------ |
| Commits       | GraphQL `totalCommitContributions`    | ×10                |
| Merged PRs    | `pullRequests(states: MERGED)`        | ×65                |
| PR Reviews    | `totalPullRequestReviewContributions` | ×40                |
| Closed Issues | `issues(states: CLOSED)`              | ×30                |
| Repos         | `repositories.totalCount`             | ×120               |
| Stars         | Sum across top repos                  | fame               |
| Followers     | `followers.totalCount`                | fame               |
| Streak        | From contribution calendar            | ×8/day             |
| Account Age   | Tenure multiplier                     | +5%/year (max 75%) |

**XP formula:**

```
craftXP = commits×10 + issues×30 + PRs×65 + reviews×40 + repos×120
tenureMult = 1 + min(years, 15) × 0.05
comboMult = 1 + min(streak, 365) / 365 × 0.25
totalXP = craftXP × tenureMult × comboMult + streak×8 + fameXP
level = floor(sqrt(totalXP / 100))
```

**Class system (by primary language):**

| Language       | Class          |
| -------------- | -------------- |
| Python         | Automancer     |
| Bash           | Scriptlord     |
| Go             | Gopher Knight  |
| YAML/Terraform | Architect      |
| Dockerfile     | Container Mage |
| JavaScript     | Web Weaver     |

**SVG design:**

- Dark card (#0d1117 bg) with #00D4FF accent glow
- Character name, class, level, rarity badge
- XP progress bar with animated fill
- Key stats (commits, PRs, issues, stars)
- Animated glow pulse on level (CSS keyframes)
- Respects `prefers-reduced-motion`

**Integration:**

```python
# scripts/generators/rpg_card.py
def render(username: str, token: str) -> str:
    """Fetch GitHub data, compute RPG stats, return SVG string."""
    data = _fetch_github_data(username, token)
    character = _compute_character(data)
    return _render_svg(character)
```

Added to orchestrator workflow as new build target:

```yaml
python -m scripts build ascii infocard heatmap rpg_card
```

**Files to create:**

- `scripts/generators/rpg_card.py` — main generator (~200 lines)
- `scripts/generators/rpg_card.py` uses `core/github.py` for GraphQL fetch (extend existing)
- `scripts/core/theme.py` — add RPG-specific tokens (glow, rarity colors)
- `scripts/tests/test_rpg_card.py` — tests for XP computation + class mapping

**README placement:** Below the ASCII portrait + info card table, before social links.

```md
### `mahesh@github ~ $ cat ~/.class`

<img src="./assets/rpg-card.svg" width="500" alt="RPG character card — Automancer Level 12" />
```

### 1B. Pac-Man Contribution Graph

**What:** Replace the snake animation with a Pac-Man game that plays over your actual contribution grid. Pac-Man eats dots (contributions), ghosts chase, power pellets on high-activity days.

**How:** Use [abozanona/pacman-contribution-graph](https://github.com/abozanona/pacman-contribution-graph) — drop-in GitHub Action, Node24 runtime, 6 games available.

**Integration:** Add step to orchestrator workflow:

```yaml
- uses: abozanona/pacman-contribution-graph@main
  with:
    github_user_name: ${{ github.repository_owner }}
    games: "pacman"
    hide_month_labels: "false"
```

Push SVGs to output branch, embed in README with `<picture>` for dark/light.

**README section replaces snake:**

```md
### `mahesh@github ~ $ cat /dev/contribution | pacman`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/pacman-dark.svg" />
  <img alt="GitHub Contribution Pac-Man" src="./assets/pacman.svg" />
</picture>
```

**Files to modify:**

- `.github/workflows/profile-orchestrator.yml` — add pacman step
- `README.md` — replace snake section with pacman
- Remove snake references from workflow

---

## Phase 2: Structural (from original plan)

| Priority | Task                         | Status  |
| -------- | ---------------------------- | ------- |
| P0       | Fix trophy section (API 402) | ✅ Done |
| P0       | Fix quote section            | ✅ Done |
| P0       | Deduplicate metrics image    | ✅ Done |
| P1       | Tech icons icoziv round      | ✅ Done |
| P1       | Social badges icoziv round   | ✅ Done |
| P1       | Visitor counter              | ✅ Done |
| P2       | Add "Now" section            | ✅ Done |
| P2       | Blog auto-update             | ✅ Done |
| P2       | CI health badge              | ✅ Done |
| P2       | Actions hardening            | ✅ Done |

## Phase 3: Cleanup (parallel with Phase 1)

| Task                                        | Effort | Status |
| ------------------------------------------- | ------ | ------ |
| Delete old superseded scripts               | 5 min  | ⬜     |
| Delete old superseded tests                 | 5 min  | ⬜     |
| Remove snake workflow (replaced by Pac-Man) | 2 min  | ⬜     |
