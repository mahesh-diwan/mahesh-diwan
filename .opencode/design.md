# README Redesign — Design Spec

## Goal

Redesign GitHub profile README for "creative pop" visual impact while preserving the terminal aesthetic (`#0d1117` bg, `#00D4FF` accent, Fira Code monospace, `$` prompt headings). Use icoziv icons exclusively for consistency.

## Visual Identity

- **Font**: Fira Code (primary monospace), JetBrains Mono (fallback) via CSS `@import` in SVGs
- **Palette**: `#0d1117` (bg), `#00D4FF` (cyan accent), `#161b22` (secondary bg), `#8b949e` (muted text)
- **Icons**: icoziv (`https://i.icoziv.workers.dev/icons?i=...`) — rounded, gradient, consistent sizing
  - Social: 32px
  - Tech stack: 36px

## Structure

| #   | Section                         | Style                                   | Source    |
| --- | ------------------------------- | --------------------------------------- | --------- |
| 1   | Header banner                   | capsule-render waving + typing SVG      | existing  |
| 2   | Contribution heatmap            | SVG from `update-profile-art` workflow  | existing  |
| 3   | Profile views + visitor counter | komarev ghpvc + visitor badge           | modified  |
| 4   | Agent-readable notice           | AGENTS.md / llms.txt links              | unchanged |
| 5   | ASCII portrait + Info card      | side-by-side table                      | existing  |
| 6   | Social links                    | icoziv icons in terminal prompt section | updated   |
| 7   | Activity graph                  | github-readme-activity-graph            | existing  |
| 8   | Snake animation                 | `<picture>` dark mode toggle            | existing  |
| 9   | Tech stack                      | icoziv icons                            | updated   |
| 10  | Blog posts                      | markdown table                          | existing  |
| 11  | Recent activity                 | recent PRs/commits log                  | **new**   |

## Recent Activity Section (New)

Borrow pattern from guilyx: embed a text log of recent contributions (merged PRs, issues) below the snake section.
Generate via the `metrics` workflow or a lightweight GitHub action.

## Icon Audit

- ✅ Social icons: icoziv (linkedin, github, twitter/x, instagram, hashnode)
- ✅ Tech stack: icoziv (aws, terraform, docker, kubernetes, jenkins, githubactions, python, bash, go, prometheus, grafana, nginx, ansible, git, linux, ubuntu)

## Acceptance Criteria

1. All icons use icoziv exclusively (no simple-icons mixed in)
2. Single font family across all rendered SVGs
3. No plain text/plain sections without terminal prompt headers
4. Recent activity section adds social proof without clutter
5. All existing automated assets retained

## Non-Goals

- Background image hero section
- Portfolio-style bio paragraph
- Contact form or email capture
