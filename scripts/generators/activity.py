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
        return (
            f"- commented on #{num} → {repo}"
            if num is not None
            else f"- commented → {repo}"
        )
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


def render(
    output_path: str = "assets/recent-activity.svg", token: str | None = None
) -> None:
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
