# Gamified GitHub Contribution Graphs — Technical Research

> Date: 2026-08-06
> Purpose: Evaluate feasibility for integration into existing GitHub Actions workflows

## Comparison Table

| Project                                 | Language        | Output    | GitHub Action        | API        | Themes                                   | Stars | Maturity     |
| --------------------------------------- | --------------- | --------- | -------------------- | ---------- | ---------------------------------------- | ----- | ------------ |
| **Platane/snk**                         | TypeScript/Bun  | SVG + GIF | ✅ Docker-based      | GraphQL v4 | Palette, colors, dark/light              | 6k    | High         |
| **abozanona/pacman-contribution-graph** | TypeScript/Node | SVG only  | ✅ Node24            | GraphQL v4 | github, github-dark, gitlab, gitlab-dark | 167   | High         |
| **sapthesh/Mario-Contribution-Graph**   | Python          | SVG only  | ✅ Python script     | GraphQL v4 | CSS-level customization                  | 0     | Low/new      |
| **README-Arcade**                       | Unknown         | SVG       | ❌ No action yet     | Unknown    | Unknown                                  | 1     | Concept only |
| **AnthonyBSong/git-pacman**             | TypeScript      | SVG only  | ✅ GitHub Action     | GraphQL v4 | Inline sprites (customizable)            | 10    | Medium       |
| **DuyetBKU/viz-pacman-github-profile**  | TypeScript      | SVG only  | ✅ Fork of abozanona | GraphQL v4 | 12 themes (6 families x light/dark)      | 1     | Fork         |

---

## 1. Platane/snk (Snake Game)

**Repo:** https://github.com/Platane/snk  
**Stars:** 6,000+ | **Forks:** 2,300+ — the original, most mature project in this space.

### Architecture

- **GitHub Action:** Docker-based (`docker://platane/snk@sha256:...`). Runs in a container, not node-based.
- **Also available as:** npm package (`generate-snake-animation`), CLI via `npx`, or Docker image directly.
- **Runtime:** Bun/TypeScript monorepo with packages for solver, SVG rendering, and GitHub API.

### Data Source

- **GitHub GraphQL API v4** — fetches `contributionsCollection.contributionCalendar.contributionDays`.
- Supports **GitHub, GitLab, and Forgejo/Codeberg**.
- Uses `github.token` by default; supports personal access tokens for private data.

### Rendering

- **Output formats:** SVG (animated `<animateMotion>`) and GIF.
- SVG-only variant available: `Platane/snk/svg-only@v3` (faster, no GIF encoding).
- Snake path uses a **solver algorithm** that generates an orderly path through all active cells.
- Colors fully customizable: palette presets (`github`, `github-dark`, `github-light`) or individual `color_snake`, `color_dots`, `color_background`.

### Integration

```yaml
- uses: Platane/snk@v3
  with:
    github_user_name: ${{ github.repository_owner }}
    outputs: |
      dist/github-snake.svg
      dist/github-snake-dark.svg?palette=github-dark
      dist/ocean.gif?color_snake=orange&color_dots=#bfd6f6,#8dbdff,#64a1f4,#4b91f1,#3c7dd9&color_background=#aaaaaa
```

### Self-hosting

- Fully self-hosted. Outputs to `dist/`, push to `output` branch via separate step.
- SVG served via `raw.githubusercontent.com`.

### Customization

- Palettes: `github`, `github-dark`, `github-light`
- Per-element colors: `color_snake`, `color_dots` (comma-separated, 5 colors), `color_background`
- Dark mode via GitHub `<picture>` syntax with `prefers-color-scheme`

### Key Insight

- Most battle-tested. 6k stars, active maintenance, 291 commits.
- SVG output is lightweight, self-contained, no external assets.
- GIF output adds ~100KB+ but works everywhere.

---

## 2. abozanona/pacman-contribution-graph (Pac-Man + 5 more games)

**Repo:** https://github.com/abozanona/pacman-contribution-graph  
**Stars:** 167 | **Forks:** 81

### Architecture

- **GitHub Action:** Node24-based (`using: node24`, `main: github-action/dist/index.js`).
- **Also available as:** npm package (`pacman-contribution-graph`), CLI tool, or CDN script.
- **Runtime:** TypeScript + Webpack, bundled to `dist/pacman-contribution-graph.min.js`.

### Data Source

- **GitHub GraphQL API v4** — same `contributionsCollection.contributionCalendar` query.
- Supports **GitHub and GitLab**.
- Private contributions: pass `githubSettings: { accessToken: 'your_token' }`.

### Games Available (6 total)

| Game          | Description                                   |
| ------------- | --------------------------------------------- |
| Pac-Man       | Eats contributions, ghosts chase              |
| Breakout      | Ball bounces breaking contribution bricks     |
| Galaga        | Ship shoots lasers at contribution grid       |
| Puzzle Bobble | Cannon fires bubbles to pop matching clusters |
| Bomberman     | Two bombers blast contribution cells          |
| Minesweeper   | Solver clears cells, flags mines              |

### Rendering

- **Output:** Animated SVG only (no GIF).
- SVG uses `<animateMotion>`, `<animate>`, `<animateTransform>` for gameplay animation.
- Contribution levels mapped to game elements:
  - NONE = empty space/wall
  - FIRST_QUARTILE = small pellet (1pt)
  - SECOND_QUARTILE = medium pellet (2pt)
  - THIRD_QUARTILE = large pellet (5pt)
  - FOURTH_QUARTILE = power pellet (ghost-eating mode)

### Integration

```yaml
- uses: abozanona/pacman-contribution-graph@main
  with:
    github_user_name: ${{ github.repository_owner }}
    games: "pacman,breakout"
    hide_month_labels: "false"
```

Push SVGs to output branch via `crazy-max/ghaction-github-pages@v3.1.0`.

### Customization

- Themes: `github`, `github-dark`, `gitlab`, `gitlab-dark`
- Pac-Man player style: `opportunistic`, `conservative`, `aggressive`
- Scenario mode for testing: `full`, `empty`, `random`, `checkerboard`, `gradient`, `streaks`
- Show/hide month labels
- Callbacks: `svgCallback`, `gameOverCallback`, `pointsIncreasedCallback`, `gameStatsCallback`

### Self-hosting

- Fully self-hosted. Same output-branch pattern.
- npm install for local use: `npm install pacman-contribution-graph`

### Key Insight

- Most feature-rich: 6 games, multiple themes, scenario testing mode.
- Node24 runtime means faster startup than Docker-based snk.
- SVG-only (no GIF), but SVGs animate natively in browsers.
- 206 commits, actively maintained.

---

## 3. sapthesh/Mario-Contribution-Graph (Mario Parkour)

**Repo:** https://github.com/sapthesh/Mario-Contribution-Graph  
**Stars:** 0 | **Forks:** 0 — very new (created April 2026).

### Architecture

- **GitHub Action:** Python script (`generate_mario.py`) run directly in workflow.
- **Runtime:** Python 3.x — no npm, no build step. Single-file script (~170 lines).
- **Dependencies:** Only Python stdlib (`os`, `json`, `urllib.request`). Zero external deps.

### Data Source

- **GitHub GraphQL API v4** — same contribution calendar query.
- Fetches via `urllib.request` with Bearer token auth.
- Uses `GITHUB_TOKEN` and `GITHUB_ACTOR` env vars from workflow.

### Rendering

- **Output:** Animated SVG only (no GIF).
- 100% pure SVG — no external images, bypasses GitHub Camo proxy.
- All sprites drawn as `<rect>` pixel grids in `<defs>`, referenced via `<use>`.
- Animation via `<animateMotion>` along a computed parkour path + `<animate>` for coins/flag.

### Parkour Physics

The path is computed mathematically:

1. Mario starts at a Warp Pipe (left side)
2. For each week column, find the **highest non-empty row** (lowest `y` position)
3. Draw quadratic Bezier curves (`Q` commands) to jump between contribution peaks
4. **Gap detection:** 4+ empty weeks triggers a high jump for a bonus coin
5. End sequence: jump to flagpole → slide down → walk to Castle → "LEVEL CLEAR!" text flash
6. Total animation duration: 20 seconds (configurable via `animation_duration`)

### Integration

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: "3.x"
- name: Generate Mario SVG
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_ACTOR: ${{ github.repository_owner }}
  run: python generate_mario.py
```

Commits SVG directly to repo (no separate output branch needed).

### Customization

- **Speed:** `animation_duration` variable (default 20s)
- **Character:** Edit `mario_pixels` array to draw any pixel character
- **Theme:** Modify CSS in `svg_elements` (sky color, ground color, etc.)
- **Coins:** Level 4 contribution days spawn spinning coins with collection animation

### Self-hosting

- Simplest to self-host: copy `generate_mario.py`, add workflow, done.
- No npm install, no Docker, no build step.

### Key Insight

- Zero dependencies. Single Python file. Easiest to integrate.
- Less polished than abozanona (0 stars, no themes, no dark mode).
- Good candidate for customization — the code is simple enough to fork and modify.
- SVG is self-contained with inline pixel sprites.

---

## 4. README-Arcade (Embeddable Games)

**Repo:** https://github.com/AshrafMorningstar/README-Arcade  
**Stars:** 1 | **Forks:** 0

### Architecture

- **Concept project** — README describes the vision but only has `.gitignore` and `README.md`.
- No actual source code, no workflow files, no implementation.
- Described as using "GitHub Actions to process game logic and update an SVG image."

### Claims (unverified)

- API: `initGame(config)`, `updateFrame(input)`, `renderLeaderboard()`
- Snake game embeddable via `https://readme-arcade.vercel.app/api/snake?user=yourname`
- Vercel serverless endpoint model

### Status

- **Not usable.** Pure concept/documentation. 2 commits only.
- The Vercel URL is likely dead.

### Key Insight

- Interesting concept: serverless game engine generating SVGs on-demand.
- Not implemented. Skip for integration purposes.

---

## 5. AnthonyBSong/git-pacman (Alternative Pac-Man)

**Repo:** https://github.com/AnthonyBSong/git-pacman  
**Stars:** 10 | **Forks:** 1

### Architecture

- **GitHub Action:** Uses `AnthonyBSong/git-pacman@main` (or `@v1`).
- TypeScript monorepo with packages: `svg-creator`, `github-api`, `action`.
- Sprites stored as separate SVG files in `assets/sprites/`.

### Rendering

- **Output:** Animated SVG only.
- Active days become dots or **cherries** (~2.5% of active days are cherries).
- **DFS traversal** computes path through all active cells, maximizing maze wall placement.
- Pac-Man moves along path eating dots/cherries, ghosts trail behind.
- All sprites render inline (self-contained SVG).

### Customization

- Fork and edit sprite SVGs in `assets/sprites/`:
  - `pacman.svg` (14×14px)
  - `ghost_{right,left}_{blue,red,pink,yellow}.svg`
  - `dot.svg`, `cherry.svg`, `empty.svg`

### Integration

```yaml
- uses: AnthonyBSong/git-pacman@v1
  with:
    github_user_name: ${{ github.repository_owner }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    svg_out_path: dist/pacman.svg
```

### Key Insight

- Cleaner code than abozanona's older forks. Better sprite system.
- Fewer features (1 game, no themes) but easier to customize sprites.
- Good if you want a simple Pac-Man with custom art.

---

## 6. DuyetBKU/viz-pacman-github-profile (Enhanced Pac-Man Fork)

**Repo:** https://github.com/DuyetBKU/viz-pacman-github-profile  
**Stars:** 1

### Architecture

- Fork of abozanona with enhancements.
- **12 color themes** (6 families × light/dark):
  - GitHub, GitLab, React, Dracula, Solarized, Monokai
- Optional **sound effects** (classic Pac-Man audio).
- Performance: 60 FPS canvas, 5 FPS SVG output.
- Bundle: 50KB minified (~15KB gzip).

### Key Insight

- Best theme selection of any Pac-Man variant.
- Sound effects are a nice differentiator.
- Fork risk: may fall behind upstream.

---

## Feasibility Matrix for GitHub Actions Integration

| Criteria               | snk           | abozanona   | Mario            | git-pacman      |
| ---------------------- | ------------- | ----------- | ---------------- | --------------- |
| **Drop-in Action**     | ✅ Docker     | ✅ Node24   | ⚠️ Python script | ✅ Action       |
| **Zero config**        | ✅            | ✅          | ⚠️ Copy script   | ✅              |
| **Dark mode**          | ✅            | ✅          | ❌               | ❌              |
| **Output branch**      | Manual step   | Manual step | Direct commit    | Manual step     |
| **Multiple games**     | ❌ Snake only | ✅ 6 games  | ❌ Mario only    | ❌ Pac-Man only |
| **Customization**      | High          | High        | Medium           | Medium          |
| **Self-contained SVG** | ✅            | ✅          | ✅               | ✅              |
| **Dependencies**       | Docker        | Node 24     | Python stdlib    | Node            |
| **GitHub API**         | GraphQL v4    | GraphQL v4  | GraphQL v4       | GraphQL v4      |

## Recommendation for Existing Workflow Integration

**Easiest path:** `abozanona/pacman-contribution-graph@main` — it's a proper GitHub Action with Node24 runtime, 6 games, themes, and dark mode support. Add one step to your workflow, push SVGs to an output branch.

**Simplest path:** `sapthesh/Mario-Contribution-Graph` — copy `generate_mario.py` into your repo, add a Python step. Zero external dependencies, but less polish.

**Most battle-tested:** `Platane/snk@v3` — Docker-based, 6k stars, supports SVG+GIF, Forgejo/GitLab too. Heavier but proven.

All three use the same data source (GitHub GraphQL API v4 contribution calendar) and output self-contained animated SVGs suitable for README embedding.
