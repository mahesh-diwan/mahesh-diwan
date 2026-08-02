#!/usr/bin/env python3
"""
Scrape public GitHub contribution calendar.
Handles both old SVG rect structure and new HTML table structure.
No token needed — reads the public HTML fragment.
"""

import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "mahesh-diwan"
URL = f"https://github.com/users/{USERNAME}/contributions"


def deduplicate_days(days):
    """Sort and deduplicate contribution days by date, keeping max level.

    Args:
        days: List of dicts with ``date`` (str) and ``level`` (int) keys.

    Returns:
        Sorted list with duplicates removed (max level wins per date).
    """
    days.sort(key=lambda d: d["date"])
    seen = {}
    for d in days:
        date = d["date"]
        if date not in seen or d["level"] > seen[date]["level"]:
            seen[date] = d
    days = list(seen.values())
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    """Compute total, streaks, best day, and monthly totals.

    Args:
        days: List of dicts with ``date`` and ``level`` keys (sorted, deduped).

    Returns:
        Dict with ``total``, ``longest_streak``, ``current_streak``,
        ``best_day``, and ``monthly_totals``.
    """
    total = sum(d["level"] for d in days)
    longest_streak = 0
    streak = 0
    best_day = {"date": None, "level": 0}

    for d in days:
        if d["level"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0
        if d["level"] > best_day["level"]:
            best_day = d

    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["level"]

    return {
        "total": total,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
    }


def fetch():
    """Scrape the public GitHub contribution calendar and save to JSON.

    Fetches ``https://github.com/users/{USERNAME}/contributions``, parses
    the HTML (handling both 2023+ table structure and older SVG rect
    layout, with regex fallback), and writes ``data/contributions.json``
    containing per-day levels, streaks, and monthly totals.

    Raises:
        requests.HTTPError: If the GitHub page returns a non-2xx status.
    """
    os.makedirs("data", exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html",
    }

    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []

    # Try new HTML table structure first (2023+)
    table_cells = soup.find_all(
        "td", class_=lambda x: x and "ContributionCalendar-day" in x
    )

    if table_cells:
        print(f"Found {len(table_cells)} cells in new table structure")
        for cell in table_cells:
            date = cell.get("data-date")
            level_str = cell.get("data-level", "0")
            if date:
                days.append({"date": date, "level": int(level_str)})
    else:
        # Fallback to old SVG rect structure
        print("Falling back to old SVG rect structure...")
        for rect in soup.find_all("rect", class_="ContributionCalendar-day"):
            date = rect.get("data-date")
            level_str = rect.get("data-level", "0")
            if date:
                days.append({"date": date, "level": int(level_str)})

    # If still empty, try regex parsing as last resort
    if not days:
        print("Trying regex fallback...")
        pattern = r'data-date="([0-9]{4}-[0-9]{2}-[0-9]{2})"[^>]*data-level="([0-9])"'
        matches = re.findall(pattern, resp.text)
        for date, level in matches:
            days.append({"date": date, "level": int(level)})

    if not days:
        print(
            "WARNING: No contribution data found. GitHub may have changed their page structure."
        )
        print("Response preview (first 1000 chars):")
        print(resp.text[:1000])

    # Sort and deduplicate
    days = deduplicate_days(days)
    stats = compute_stats(days)

    data = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_contributions": stats["total"],
        "current_streak": stats["current_streak"],
        "longest_streak": stats["longest_streak"],
        "best_day": stats["best_day"],
        "monthly_totals": stats["monthly_totals"],
        "days": days,
    }

    with open("data/contributions.json", "w") as f:
        json.dump(data, f, indent=2)

    print(
        f"Fetched {len(days)} days, total={total}, longest_streak={longest_streak}, current_streak={current_streak}"
    )


if __name__ == "__main__":
    fetch()
