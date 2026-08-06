#!/usr/bin/env python3
"""Unified CLI entrypoint for all profile art generators.

Usage:
    python -m scripts build               # Generate all assets
    python -m scripts build heatmap       # Generate one asset
    python -m scripts fetch               # Fetch contribution data only
    python -m scripts test                # Run tests
"""

import argparse
import sys
from pathlib import Path

# Ensure scripts/ is on path for relative imports
sys.path.insert(0, str(Path(__file__).parent))


def cmd_build(args):
    """Generate all assets (or a specific one)."""
    from core.github import fetch
    from generators.activity import render as render_activity
    from generators.header import render as render_header
    from generators.heatmap import render as render_heatmap

    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    target = args.target if hasattr(args, "target") else None

    if target in (None, "heatmap"):
        data = fetch()
        render_heatmap(data)
    if target in (None, "header"):
        render_header()
    if target in (None, "activity"):
        render_activity()


def cmd_fetch(args):
    """Fetch contribution data only."""
    from core.github import fetch

    fetch()


def cmd_test(args):
    """Run tests."""
    import pytest

    sys.exit(pytest.main(["-v", "scripts/"]))


def main():
    parser = argparse.ArgumentParser(description="Profile art generator")
    sub = parser.add_subparsers(dest="command")

    build_p = sub.add_parser("build", help="Generate assets")
    build_p.add_argument("target", nargs="?", choices=["heatmap", "header", "activity"])

    sub.add_parser("fetch", help="Fetch contribution data")
    sub.add_parser("test", help="Run tests")

    args = parser.parse_args()

    if args.command == "build":
        cmd_build(args)
    elif args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "test":
        cmd_test(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
