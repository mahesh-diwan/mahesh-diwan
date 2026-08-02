# GitHub README Redesign — Execution Plan

Source: Research of 10 exemplary GitHub profiles + audit of mahesh-diwan profile

## Priority Checklist

| Priority | Task                                        | File        | Effort | Status |
| -------- | ------------------------------------------- | ----------- | ------ | ------ |
| 🔴 P0    | Fix trophy section                          | `README.md` | 5 min  | ⬜     |
| 🔴 P0    | Fix quote section                           | `README.md` | 5 min  | ⬜     |
| 🔴 P0    | Deduplicate metrics image                   | `README.md` | 5 min  | ⬜     |
| 🟡 P1    | Tech icons — skill-icons/icoziv round, 36px | `README.md` | 15 min | ⬜     |
| 🟡 P1    | Social badges — icoziv round, 32px          | `README.md` | 10 min | ⬜     |
| 🟡 P1    | GitHub stats card with #00D4FF accent       | `README.md` | 10 min | ⬜     |
| 🟡 P1    | Visitor counter badge                       | `README.md` | 2 min  | ⬜     |
| 🟢 P2    | Add "Now" section                           | `README.md` | 10 min | ⬜     |
| 🟢 P2    | Blog auto-update (Hashnode RSS)             | workflow    | 30 min | ⬜     |
| 🟢 P2    | CI health badge                             | `README.md` | 2 min  | ⬜     |
| 🟢 P2    | Actions hardening (retries, SVG validation) | workflows   | 30 min | ⬜     |

## Key Decisions (from brainstorming)

- Font: **Fragment Mono** (not Fira Code) — applied to all 3 SVG scripts + @import
- Icons: **icoziv** (not skill-icons) — covers social + tech with gradient/3D
- Color: #0d1117 (bg), #00D4FF (cyan accent), #161b22 (secondary bg), #8b949e (muted)
- Terminal aesthetic: KEPT — all headers as `$` prompt commands
- Style: Creative pop — animated SVGs, staggered reveals, gradient text

## Completed

- ✅ Font swap to Fragment Mono in all 3 scripts
- ✅ SVGs regenerated via workflows
- ✅ Visitor counter added (komarev with labelColor=#161b22)
- ✅ Activity section added (metrics.svg with title `cat /dev/activity`)
- ✅ Static contribution blocks removed (the monthly table)
- ✅ icoziv icons adopted for social + tech
