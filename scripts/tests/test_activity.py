#!/usr/bin/env python3
"""Tests for the recent-activity generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.activity import FALLBACK_LINE, _parse_events, build_svg


def _event(etype: str, **payload) -> dict:
    ev = {"type": etype, "repo": {"name": "mahesh-diwan/flexfetch"}, "payload": {}}
    ev["payload"].update(payload)
    return ev


def _pr_event(action: str, number: int) -> dict:
    ev = _event("PullRequestEvent")
    ev["payload"] = {"action": action, "pull_request": {"number": number}}
    return ev


class TestParseEvents:
    def test_push_multiple_commits(self):
        events = [_event("PushEvent", size=3, commits=[{}, {}, {}])]
        assert _parse_events(events) == ["- pushed 3 commits → flexfetch"]

    def test_push_single_commit_singular(self):
        events = [_event("PushEvent", size=1, commits=[{}])]
        assert _parse_events(events) == ["- pushed 1 commit → flexfetch"]

    def test_pr_opened(self):
        assert _parse_events([_pr_event("opened", 12)]) == [
            "- opened PR #12 → flexfetch"
        ]

    def test_pr_merged(self):
        assert _parse_events([_pr_event("merged", 12)]) == [
            "- merged PR #12 → flexfetch"
        ]

    def test_issue_comment(self):
        ev = _event("IssueCommentEvent", action="created", issue={"number": 5})
        assert _parse_events([ev]) == ["- commented on #5 → flexfetch"]

    def test_release(self):
        ev = _event("ReleaseEvent", action="published", release={"tag_name": "v0.3.1"})
        assert _parse_events([ev]) == ["- released v0.3.1 → flexfetch"]

    def test_ignores_other_event_types(self):
        star = _event("StarEvent", action="created", starred_at="x")
        fork = _event("ForkEvent", forkee={"id": 1})
        assert _parse_events([star, fork]) == [FALLBACK_LINE]

    def test_limit_applies(self):
        events = [_event("PushEvent", size=2, commits=[{}, {}]) for _ in range(10)]
        lines = _parse_events(events)
        assert len(lines) == 5

    def test_malformed_event_no_crash(self):
        assert _parse_events([{}]) == [FALLBACK_LINE]
        assert _parse_events([{"type": "PushEvent"}]) == ["- pushed 1 commit → unknown"]

    def test_empty_returns_fallback(self):
        assert _parse_events([]) == [FALLBACK_LINE]


class TestBuildSvg:
    def test_contains_prompt_and_lines(self):
        svg = build_svg(["- pushed 3 commits → flexfetch"])
        assert "tail -f ~/.github.log" in svg
        assert "pushed 3 commits" in svg
        assert svg.startswith("<svg") and svg.endswith("</svg>")

    def test_escapes_special_chars(self):
        svg = build_svg(["- released v1.0 & <beta>"])
        assert "&amp;" in svg
        assert "&lt;" in svg

    def test_smil_only(self):
        svg = build_svg([FALLBACK_LINE])
        assert "<animate" in svg
        assert "@keyframes" not in svg
        assert "@import" not in svg
        assert "fonts.googleapis.com" not in svg
