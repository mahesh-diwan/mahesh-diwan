# Research: RPG-Style GitHub Profile Card Generators

## 1. GitLevel (GavinnnTann/GitLevel)

### What it is

Serverless Vercel app that generates an animated RPG character card SVG from GitHub activity. Class, level, XP, fame, combo streak, rarity, badges, season rank.

### Deployment model

- **Platform**: Vercel serverless functions (`api/*.js`)
- **Zero dependencies** — uses only `fetch` and template strings
- **One env var needed**: `GITHUB_TOKEN` (public read-only PAT)
- **Optional**: Upstash Redis for durable cache, rate limiting, usage stats
- **Self-hostable**: Yes, one-click Vercel deploy button, ~2 minutes
- **vercel.json**: Functions set to `maxDuration: 15s`, rewrite `/u/:username` → `/u.html`

### GitHub API endpoints (GraphQL)

Single GraphQL query to `https://api.github.com/graphql`:

```graphql
query gitlevel($login: String!, $seasonFrom: DateTime!, $seasonTo: DateTime!) {
  user(login: $login) {
    name
    login
    createdAt
    followers {
      totalCount
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestReviewContributions
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
    season: contributionsCollection(from: $seasonFrom, to: $seasonTo) {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
      totalRepositoryContributions
    }
    mergedPRs: pullRequests(states: MERGED) {
      totalCount
    }
    closedIssues: issues(states: CLOSED) {
      totalCount
    }
    repositories(
      first: N
      ownerAffiliations: OWNER
      isFork: false
      orderBy: { field: STARGAZERS, direction: DESC }
    ) {
      totalCount
      nodes {
        stargazers {
          totalCount
        }
        languages(first: M, orderBy: { field: SIZE, direction: DESC }) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
  }
}
```

**Tier fallback**: Queries start at `repos: 100, langs: 10`, step down to `40/6` then `15/4` on resource-limit or timeout errors. Total fetch budget: 8s across all tiers.

### What stats it uses

| Stat          | Source                                                    | Period         |
| ------------- | --------------------------------------------------------- | -------------- |
| Commits       | `totalCommitContributions + restrictedContributionsCount` | Last 12 months |
| Merged PRs    | `pullRequests(states: MERGED).totalCount`                 | Lifetime       |
| PR Reviews    | `totalPullRequestReviewContributions`                     | Last 12 months |
| Closed Issues | `issues(states: CLOSED).totalCount`                       | Lifetime       |
| Repos Created | `repositories.totalCount`                                 | Lifetime       |
| Stars         | Sum of `stargazers.totalCount` across top repos           | Lifetime       |
| Followers     | `followers.totalCount`                                    | Lifetime       |
| Streak        | Calculated from contribution calendar                     | Current        |
| Languages     | Aggregated from repo language bytes (owned, non-fork)     | Lifetime       |
| Account Age   | `Date.now() - Date.parse(createdAt)`                      | Lifetime       |

### XP formula

```
craftXP = commits×10 + closedIssues×30 + mergedPRs×65 + reviews×40 + reposCreated×120
tenureMult = 1 + min(years, 15) × 0.05           // up to +75%
comboMult = 1 + min(streak, 365) / 365 × 0.25    // up to +25%
streakXP = streak × 8
fameXP = min(40000, 48 × sqrt(followers + stars))
totalXP = craftXP × tenureMult × comboMult + streakXP + fameXP
level = floor(sqrt(totalXP / 100))
```

### SVG rendering

- **Server-side only** — no client JS
- Handler returns `Content-Type: image/svg+xml`
- SVG built from template strings in `src/renderCard.js`
- Animated CSS keyframes (crest pop, rune spin, XP bar grow, glow pulse)
- Respects `prefers-reduced-motion`
- Errors always return HTTP 200 with a small error SVG (never breaks README `<img>`)

### Customization options

| Param           | Type   | Default | Notes                                                        |
| --------------- | ------ | ------- | ------------------------------------------------------------ |
| `username`      | string | —       | **Required**                                                 |
| `theme`         | enum   | `volt`  | `volt`, `midnight`, `sunset`, `matrix`, `ice`, `transparent` |
| `exclude_langs` | string | —       | Comma-separated (e.g. `HTML,CSS`)                            |
| `hide_border`   | bool   | `false` |                                                              |
| `title_color`   | hex    | theme   |                                                              |
| `text_color`    | hex    | theme   |                                                              |
| `bg_color`      | hex    | theme   | `00000000` = transparent, or `deg,c1,c2` gradient            |
| `border_color`  | hex    | theme   |                                                              |
| `glow_color`    | hex    | theme   | Neon glow filter                                             |
| `border_radius` | number | `14`    | Clamped 0–60                                                 |
| `card_width`    | int    | `500`   | Clamped 440–800                                              |
| `badges`        | int    | `4`     | 0–9, how many badges shown                                   |
| `cache_seconds` | int    | `21600` | Clamped 3600–86400                                           |
| `animation`     | bool   | `true`  | `false` = static                                             |
| `creator`       | bool   | `true`  | `false` = show real class                                    |

### API endpoints

- `GET /api/card?username=X` — SVG character card (always 200)
- `GET /api/profile?username=X` — JSON character data (real status codes)
- `GET /u/USERNAME` — HTML character sheet page
- `GET /api/stats` — `{ enabled, uniqueUsers, cardsServed }` (requires Upstash)

### Key source files

- `api/card.js` — Vercel handler
- `src/engine.js` — XP computation, `computeCharacter()`
- `src/fetchProfile.js` — GraphQL fetch with tier fallback + caching
- `src/renderCard.js` — SVG template builder
- `src/github.js` — Token selection, GraphQL wrapper
- `src/achievements.js` — Badge families
- `src/seasons.js` — Season rank computation
- `src/themes.js` — Theme definitions

### Verdict

**Excellent for our use case.** Well-structured, zero deps, easy to fork and customize. The XP/level/class system is already a full RPG framework. The card design is polished with animation support. Self-hosting is trivial (Vercel + token). Can customize themes, colors, what badges show, which languages count.

---

## 2. Developer RPG Profile Generator (Git-Roast, nandinigoyaldev)

### What it is

A React 19 + TypeScript + Vite 8 web app that roasts GitHub profiles, generates READMEs, and provides a simple badge API. **Not truly "RPG" despite the name** — more of a profile roaster with a gamification skin.

### Deployment model

- **Platform**: Vercel serverless (both frontend and API routes)
- **Frontend**: React 19, TypeScript 6, Vite 8, Recharts
- **API**: Vercel serverless functions in `api/`

### GitHub API endpoints (REST)

- `/api/github?username=X` — Fetches from `https://api.github.com/users/{user}` (REST, single call)
- `/api/badge?username=X` — SVG badge
- `/api/readme` — POST, generates markdown
- `/api/repo?url=X` — POST, audits repo health

### What stats it uses

- Public repos count
- Basic profile metadata from GitHub REST API
- PR ratios, commit history (from `/api/github`)

### SVG badge

Simple badge SVG generated server-side:

```
Grade A+ to F based on public_repos count
Shows: "Rank: {grade} | {title}"
300×40px, GitHub Dark theme colors
```

The badge logic is trivial — just grades based on repo count (A if >50, B if >20, C if >5, else F).

### Customization

- Minimal — no theme parameters on the badge endpoint
- Frontend has some UI customization but not exposed via URL params
- No RPG class/level/XP system

### Verdict

**Not useful for our purposes.** Despite the name, this is a profile roaster, not an RPG card generator. The badge API is trivial (single REST call, repo count only, no real RPG mechanics). The RPG framing is marketing, not substance.

---

## 3. Simpler Alternatives

### a) github-readme-stats (anuraghazra)

- **Stars**: 79.8k
- **Status**: ⚠️ **DEPRECATED** — successor is `stats-organization/github-stats-extended`
- **Deployment**: Vercel serverless (or GitHub Actions via `readme-tools/github-readme-stats-action`)
- **Cards**: Stats card, Top Languages card, Repo Pin card, Gist card, WakaTime card
- **Themes**: 15+ built-in themes, full color customization
- **Customization**: Extensive URL params (hide stats, show icons, card width, locale, etc.)
- **Not RPG**: Standard stats cards, no class/level/XP mechanics
- **Still works** but no longer maintained

### b) github-stats-extended (successor)

- **Status**: Actively maintained fork of github-readme-stats
- Same architecture, same Vercel deployment model
- Not RPG-themed

### c) user-statistician (cicirello)

- **Type**: GitHub Action (not a serverless app)
- **How it works**: Runs inside GitHub Actions, generates SVG, commits to repo
- **No external server needed** — fully self-contained
- **Stats**: Detailed activity summary, contribution calendar
- **Deployment**: Add workflow to `.github/workflows/`, runs on schedule
- **Good for**: Avoiding Vercel dependency entirely

### d) profile-graphics (mikhailkhorokhorin)

- **Type**: GitHub Action + CI/CD approach
- **How it works**: Runs on schedule, generates SVGs, commits `dist/*.svg` to repo
- **40 themes, 8 chart types**
- **No external servers** — GitHub serves static SVGs via CDN
- **Good for**: Full self-hosting without any external service

### e) GitHubCard (githubcard.com)

- **Type**: Web-based visual editor
- **How it works**: Drag-and-drop widgets (stats, heatmap, languages, repos) on a canvas
- **SVG/PNG export** — one cohesive card, not mismatched embeds
- **No GitHub Actions needed** — live GitHub data
- **20+ widgets**
- **Good for**: Design-first approach, non-RPG but highly customizable

---

## 4. Recommendation: Build Our Own

### Why fork GitLevel?

- It's the only project with a **real RPG system** (classes, levels, XP, rarity, badges, seasons)
- Zero dependencies — pure JS, easy to modify
- Vercel deployment is trivial
- MIT license
- Well-structured codebase (~20 source files)
- SVG rendering is server-side — works in any README

### What to customize

1. **Themes**: Add DevOps/infrastructure-themed color schemes
2. **Classes**: Map languages to DevOps roles (Bash → Scriptlord, Python → Automancer, etc.)
3. **Badges**: Add DevOps-specific badges (CI/CD Pioneer, Container Commander, etc.)
4. **Stats**: Could add GitHub Actions workflow count, release frequency

### Minimum viable fork

1. Deploy GitLevel to your own Vercel account (one-click)
2. Set custom themes in `src/themes.js`
3. Optionally modify class names in `src/classes.js`
4. Done — custom RPG card in your README

### Alternative: Build from scratch

If you want full control:

- Use the same GraphQL query pattern from GitLevel
- Serverless function (Vercel/Cloudflare Workers)
- SVG template strings
- XP formula (can copy or modify)
- Estimated effort: 2-3 days for a basic version, 1-2 weeks for full polish

### Quick start

```md
[![GitLevel](https://your-deployment.vercel.app/api/card?username=mahesh-diwan&theme=midnight)](https://your-deployment.vercel.app/u/mahesh-diwan)
```
