# scripts

CLI for fetching GitHub contribution data and rendering profile SVG assets into `assets/`.

## Usage

- `python -m scripts build` — generate all assets (heatmap, header, activity, banners) into `assets/`
- `python -m scripts build heatmap|header|activity|banners` — generate one
- `python -m scripts fetch` — fetch contribution data to `data/contributions.json`
- `python -m scripts test` — run tests

## Structure

- `scripts/core/` — shared modules (theme, svg, github, achievements)
- `scripts/generators/` — heatmap, header, activity, banners
- `scripts/tests/` — pytest suite

Run tests from repo root:

```
python -m pytest scripts/tests/ -v
```

## Automation

The profile-orchestrator workflow (`python -m scripts build` + Pac-Man action)
regenerates and commits assets daily at 06:17 UTC.
