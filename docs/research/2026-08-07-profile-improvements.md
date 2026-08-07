# Profile README & SVG improvement research

## Scope & method

Researched GitHub README image caching, SVG sanitization, and DM Mono font embedding against GitHub Docs, GitHub markup/issues, W3C/O'Reilly SVG material, and OFL text. Read this repo's README, workflow, and SVG generators first. No code changed.

## A. What can be done better

1. **Camo caches external README images ~1 year; `?v=` busts it (only for external URLs).**
   Claim: camo (GitHub's image proxy) caches by hash of the _full URL_; default `max-age=31536000` when origin sends no cache headers; it honors origin `Cache-Control`. Appending `?v=N` changes the URL → new hash → fresh fetch.
   Evidence: docs.github.com "About anonymized URLs" (curl + `curl -X PURGE`); umami#4011 (camo forwards `public, max-age=31536000`); magna-nz PR "bust camo cache with ?v=2"; humanish commit "cache-bust the README hero image URL"; hesreallyhim/github-image-cache-bust demo repo.
   Tier: primary (docs) + primary-adjacent (observed PRs). Confidence: **high**.
   Improvement: only matters for this repo's _external_ `<img>`s (capsule-render, readme-typing-svg, ghpvc, icoziv icons, actions badge). Bump `?v=` on them when you change their params. Repo-relative assets do NOT go through camo (see #2).

2. **Repo-relative `./assets/*.svg` is already the best URL form — keep it.**
   Claim: relative README images render via GitHub's raw pipeline with SVG served sanitized + correct content-type. `raw.githubusercontent.com` serves SVG as `text/plain`+nosniff and caches ~5 min/IP (stale for dynamic content). `github.com/{o}/{r}/raw/...` also works but is redundant here. `user-attachments` is for issue/comment uploads, not repo assets.
   Evidence: isaacs/github#316 (relative SVG fixed, raw serves text/plain); SO 64792450 (raw ~5 min per-IP cache); gh-aw commit 5f5f569 (raw URL form fails private repos — irrelevant, repo is public).
   Tier: secondary (issues/SO). Confidence: **high**.
   Improvement: none needed — relative paths already dodge camo's 1-yr cache, so daily workflow pushes appear fresh. No change.

3. _*GitHub sanitizes README-rendered SVGs: strips script/on* / javascript: / external `url()` and `@import`; CSS animations and SMIL survive._*
   Claim: GitHub auto-sanitizes SVGs referenced from README `<img>` (the `?sanitize=true` pipeline). Scripts, event handlers, `javascript:` URIs, external resource refs and `@import` in CSS are stripped. SMIL `<animate>` and pure CSS/SMIL animation work; foreignObject demonstrably survives (sindresorhus's css-in-readme trick renders), though some sanitizer suites claim it is stripped.
   Evidence: markup-carve/docs/svg-images.md (sanitizer drops external/url()/@import, active CSS, foreignObject); msuliq/svg_sentinel (@import = disallowed, external refs); dkod-io/dkod-engine#65 (GitHub sanitizer strips data URIs); sindresorhus/css-in-readme-like-wat (foreignObject + CSS works); nakkas github-compatibility tests ("no external resource URLs, only system fonts work"); github/markup#1160 (attribute-level stripping).
   Tier: secondary — **no first-party doc exists** for the exact rule set. Confidence: **medium-high**.
   Improvement: keep every generator SVG fully self-contained (no `@import`, no external `url()`, no fonts.googleapis.com) — current code already complies. Real bug found: `assets/profile-header.svg` declares `font-family` inside `<defs>` as bare CSS (`text { ... }`) — invalid placement, browsers ignore it; must live in a `<style>` element.

4. **Data-URI `@font-face` in `<img>`-context SVG is not reliably supported even before GitHub's sanitizer.**
   Claim: an SVG shown via `<img>` must be standalone — browsers don't fetch external resources (incl. `@import`/external fonts) in that context. Data-URI fonts are the only possible embed, and O'Reilly "Using SVG" documents "WebKit doesn't support data URIs in SVG-as-image" while Firefox does; recent reports are mixed.
   Evidence: O'Reilly dataURI-fonts chapter; SO 46307391, 20577316, 15194870; meyerweb custom-fonts test page.
   Tier: secondary (O'Reilly is authoritative-practice, still secondary). Confidence: **medium** (browser behavior; the WebKit caveat is old, current Chrome unverified).
   Improvement: don't attempt it in README SVGs (see Section B verdict).

5. **Image sizing: GitHub renders `<img>` at `max-width:100%`; explicit `width` attribute works; you cannot add `loading="lazy"` via markdown.**
   Claim: GitHub markdown sanitizer allows `<img>` with src/alt/width/height but strips `style`; width-in-px attributes scale responsively (CSS `max-width:100%`). `loading="lazy"` is not in the allowed attribute set, so it can't be added from markdown.
   Evidence: onezeronull.com (README HTML/SVG rendering notes); nakkas compatibility suite; GitHub's known HTML allowlist behavior in github/markup.
   Tier: secondary. Confidence: **medium**.
   Improvement: current `width="760"`/`width="860"` usage is correct. Keep `alt` on every image (a11y + tooltip). Don't bother trying `loading`.

6. **Alt text and badge cache headers are the remaining easy wins.**
   Claim: every generated SVG already carries `alt`. External badge services control their own camo caching; shields.io-style services set `no-cache` so they refresh. Nothing actionable except periodic `?v=` bumps.
   Evidence: docs "About anonymized URLs" (Cache-Control guidance); markup#224 (CDN caching respects origin headers).
   Tier: primary/secondary. Confidence: **high**.
   Improvement: add `?v=<date>` to external `<img>`s only when their content changes; verify with `curl -I` before trusting a new badge.

## B. Using DM Mono

1. **Embed via base64 `@font-face` data URI — NOT reliably supported.**
   Verdict: infeasible / unverified. Evidence: (a) GitHub's sanitizer is documented stripping data URIs (dkod-io#65, "data URI stripped by GitHub's SVG sanitizer") and forbidding external refs (markup-carve, svg_sentinel, nakkas "only system fonts work") — no first-party doc confirms `@font-face`/`data:` survives; (b) even unsanitized, `<img>`-context SVGs don't load external fonts and WebKit-class browsers historically ignore data-URI fonts (O'Reilly). Two independent failure points, each alone enough to break rendering. Tradeoffs: if it _did_ work, cost is ~14.5KB woff2 latin 400 (fontsource) → ~19KB base64 (+33%) per weight; needs a real on-github.com render test to ever trust it. Not worth the risk.

2. **Self-host via `@import` / font URL (e.g. cdn.jsdelivr.net) — does not work.**
   Verdict: infeasible. Evidence: sanitizer strips `@import` and external `url()` (markup-carve, svg_sentinel, nakkas); plus `<img>`-context SVGs can't fetch external resources at all (O'Reilly, SO 46307391). Two independent blockers. Tradeoffs: zero if accepted; broken glyphs if attempted.

3. **System mono fallback stack — guaranteed, zero bytes.**
   Verdict: this is the only reliable option. `font-family: "DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;` renders on every viewer OS; "DM Mono" silently falls back to the first installed system mono (macOS SFMono, Win Consolas, Linux Liberation/JetBrains via UI). Evidence: nakkas "only system fonts work"; current header already does this (just in the wrong element — see A.3).
   Tradeoffs: no real DM Mono fidelity — it's whatever mono the viewer has. Cosmetic only.

4. **OFL permits embedding; size is not the blocker; licensing is a non-issue.**
   Verdict: legal green light if you ever embed. Evidence: `google/fonts/ofl/dmmono/OFL.txt` (primary) — "Font Software ... may be bundled, embedded, redistributed" provided the license/copyright accompany; "requirement ... does not apply to any document created using the fonts." DM Mono latin woff2 ≈ 10–15KB/weight (fontsource listing; google-webfonts-helper/gwfh.mranftl.com). Subsetting to used glyphs via `fonttools pyftsubset` (fonttools.readthedocs.io, `subset` command) could cut further — but only relevant if embed becomes viable, which it isn't.

## C. Recommendation

1. Fix the one real bug: move `font-family` CSS out of `<defs>` into `<style>` in the SVG generators (core.svg helper emits `<style>`), keeping the system-mono stack with `"DM Mono"` as an inert first fallback.
2. Do NOT embed DM Mono via base64 `@font-face` or `@import`/jsdelivr — both are stripped or ignored in README `<img>` SVGs; system mono is the guaranteed rendering.
3. Keep repo-relative `./assets/*.svg` URLs — they bypass camo's 1-year cache; daily workflow commits already refresh viewers (~5-min raw cache).
4. Keep all SVGs self-contained: no `@import`, no external `url()`, no fonts.googleapis.com, SMIL-only animation (current code already complies).
5. For the _external_ camo images (capsule-render, readme-typing-svg, ghpvc, icons): when you change their params, bump `?v=` once to force a fresh camo fetch; verify the SVG renders before pushing.
6. Preserve existing good practice: `width` attribute + `alt` on every `<img>`; `<picture>` for pacman light/dark.
7. Skip `loading="lazy"` — GitHub's README sanitizer doesn't allow it from markdown.
8. Re-verify visually after the `<style>` fix by opening the profile on github.com (and in dark mode), since sanitizer behavior is undocumented first-party.

## Sources

- docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-anonymized-urls (camo, Cache-Control, PURGE)
- github.com/github/markup/issues/224 (CDN caching + origin headers)
- github.com/umami-software/umami/issues/4011 (camo default max-age=31536000)
- github.com/magna-nz/aspnetcore-debugger-mcp/pull/26 (?v=2 camo bust)
- github.com/danielgwilson/humanish commit 914680a (?v cache-bust)
- github.com/hesreallyhim/github-image-cache-bust (demo repo)
- github.com/isaacs/github/issues/316 + github/markup#556 (relative SVG, raw text/plain)
- stackoverflow.com/questions/64792450 (raw.githubusercontent ~5-min cache)
- github.com/gh-aw commit 5f5f569 (raw vs github.com/raw URL forms)
- oreillymedia.github.io/Using_SVG/extras/ch07-dataURI-fonts.html (data-URI fonts, WebKit caveat)
- github.com/sindresorhus/css-in-readme-like-wat (foreignObject renders)
- github.com/dkod-io/dkod-engine/pull/65 (GitHub sanitizer strips data URIs)
- markup-carve carve docs/svg-images.md; msuliq/svg_sentinel; nakkas github-compatibility tests
- github.com/github/markup/issues/1160 (attribute stripping)
- github.com/google/fonts/blob/main/ofl/dmmono/OFL.txt (OFL 1.1, embedding clause)
- fontsource.org/@fontsource/dm-mono (file sizes); gwfh.mranftl.com/fonts/dm-mono; fonttools.readthedocs.io (pyftsubset)
- SO 13808020, 46307391, 20577316, 15194870, 26898052 (SVG-in-img fonts/caching)
