# Visual Audit — github.com/mahesh-diwan (Playwright, 2026-08-06)

## BROKEN (remove or fix)

1. **CI badge** → `404` — references `update-profile-art.yml` workflow that was
   deleted when the orchestrator replaced it. Console error:
   `actions/workflows/update-profile-art.yml/badge.svg:0`. Fix: point at
   `profile-orchestrator.yml` or drop the badge.
2. **GitHub Stats card** (`github-readme-stats .../api?username=...`) →
   `net::ERR_BLOCKED_BY_ORB`. github-readme-stats is deprecated (2025); its
   Vercel app returns an HTML error, camo/ORB blocks it. → REMOVE.
3. **Top Languages card** (`github-readme-stats .../api/top-langs/...`) → same
   `net::ERR_BLOCKED_BY_ORB`. → REMOVE.

## WORKING (verified 200)

- capsule-render header banner, readme-typing-svg (header + thanks footer)
- contrib-heatmap.svg, mahesh-ascii.svg, info-card.svg, rpg-card.svg (renders
  "Automancer Level 12"), pacman.svg, metrics.svg
- komarev visitor counter, activity-graph, streak-stats, dev-quote
- all icoziv social + tech icons
- all local assets via raw.githubusercontent (200)

## BLOAT / DUPLICATION (README is ~400 lines, user wants shorter)

- `skills --detailed` table duplicates the info-card.svg content
- `profile --focus`, `cat ~/now.md`, `level --up` = static ASCII boxes, fake
- `quests --list` escape room + 3 Easter-egg `<details>` = cute but long
- `profile --recent-releases` shows a single release, stale
- `profile --recent-blog` shows 2024 posts (stale)
- two typing SVGs (header + footer), two social-icon rows (footer repeats
  authorized_keys)
- stats cards dead (above) — remove

## WANT (user)

- more interactive / playful
- research Pac-Man contribution graph options
- shorter, readable README
- font: DM Mono or Fragment Mono (readme-typing-svg + generated SVGs already
  use Fragment Mono; the SVG CSS @import uses DM Mono + Fragment Mono)
