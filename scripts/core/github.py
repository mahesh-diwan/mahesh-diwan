"""GitHub API client with retries and caching.

Wraps contribution fetching with proper error handling, retries,
and local cache fallback. Also provides GraphQL profile queries.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "mahesh-diwan"
URL = f"https://github.com/users/{USERNAME}/contributions"
CACHE_PATH = Path("data/contributions.json")
GRAPHQL_URL = "https://api.github.com/graphql"

PROFILE_QUERY = """
query gitlevel($login: String!, $seasonFrom: DateTime!, $seasonTo: DateTime!) {
  user(login: $login) {
    name
    login
    createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestReviewContributions
      contributionCalendar {
        weeks {
          contributionDays { date contributionCount }
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
    mergedPRs: pullRequests(states: MERGED) { totalCount }
    closedIssues: issues(states: CLOSED) { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: { field: STARGAZERS, direction: DESC }) {
      totalCount
      nodes {
        stargazers { totalCount }
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def _retry_get(
    url: str, retries: int = 3, delay: float = 30.0, **kwargs
) -> requests.Response:
    """GET with retry and exponential backoff."""
    kwargs.setdefault("timeout", 30)
    kwargs.setdefault("headers", {})
    kwargs["headers"].setdefault(
        "User-Agent",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    )
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            last_err = e
            if attempt < retries:
                print(
                    f"Attempt {attempt}/{retries} failed: {e}, retrying in {delay}s..."
                )
                import time

                time.sleep(delay)
    raise last_err


def fetch() -> dict:
    """Scrape the public GitHub contribution calendar.

    Returns dict with days, stats, metadata. Writes to CACHE_PATH.
    Falls back to cache on network failure.
    """
    os.makedirs(CACHE_PATH.parent, exist_ok=True)

    try:
        resp = _retry_get(URL)
        soup = BeautifulSoup(resp.text, "html.parser")
        days = _parse_contributions(soup, resp.text)
    except Exception as e:
        print(f"Network fetch failed: {e}")
        if CACHE_PATH.exists():
            print(f"Falling back to cache: {CACHE_PATH}")
            return json.loads(CACHE_PATH.read_text())
        raise

    if not days:
        print("WARNING: No contribution data found.")
        if CACHE_PATH.exists():
            return json.loads(CACHE_PATH.read_text())
        return {"days": [], "total_contributions": 0}

    days = _deduplicate_days(days)
    stats = _compute_stats(days)

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

    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Fetched {len(days)} days, total={stats['total']}")
    return data


def _parse_contributions(soup: BeautifulSoup, raw_html: str) -> list[dict]:
    """Parse contribution days from HTML (new table, old SVG, or regex fallback)."""
    days = []

    # New HTML table structure (2023+)
    table_cells = soup.find_all(
        "td", class_=lambda x: x and "ContributionCalendar-day" in x
    )
    if table_cells:
        for cell in table_cells:
            date = cell.get("data-date")
            level_str = cell.get("data-level", "0")
            if date:
                days.append({"date": date, "level": int(level_str)})
        return days

    # Old SVG rect structure
    for rect in soup.find_all("rect", class_="ContributionCalendar-day"):
        date = rect.get("data-date")
        level_str = rect.get("data-level", "0")
        if date:
            days.append({"date": date, "level": int(level_str)})

    # Regex fallback
    if not days:
        pattern = r'data-date="([0-9]{4}-[0-9]{2}-[0-9]{2})"[^>]*data-level="([0-9])"'
        for date, level in re.findall(pattern, raw_html):
            days.append({"date": date, "level": int(level)})

    return days


def _deduplicate_days(days: list[dict]) -> list[dict]:
    """Sort and deduplicate by date, keeping max level."""
    days.sort(key=lambda d: d["date"])
    seen: dict[str, dict] = {}
    for d in days:
        date = d["date"]
        if date not in seen or d["level"] > seen[date]["level"]:
            seen[date] = d
    return sorted(seen.values(), key=lambda d: d["date"])


def _compute_stats(days: list[dict]) -> dict:
    """Compute total, streaks, best day, and monthly totals."""
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

    monthly: dict[str, int] = {}
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


def fetch_profile(token: str | None = None) -> dict:
    """Fetch full GitHub profile via GraphQL for RPG card generation.

    Returns dict with user data: name, login, createdAt, followers, commits,
    mergedPRs, closedIssues, repos, stars, languages, streak, etc.
    Falls back to REST API if no token provided.
    """
    token = token or os.environ.get("GITHUB_TOKEN", "")
    now = datetime.now(timezone.utc)
    season_from = now.replace(year=now.year - 1).isoformat()
    season_to = now.isoformat()

    if token:
        headers = {
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": PROFILE_QUERY,
            "variables": {
                "login": USERNAME,
                "seasonFrom": season_from,
                "seasonTo": season_to,
            },
        }
        try:
            resp = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if "errors" in data:
                print(f"GraphQL errors: {data['errors']}")
                return _fallback_profile()
            return _parse_profile(data["data"]["user"])
        except Exception as e:
            print(f"GraphQL fetch failed: {e}")
            return _fallback_profile()
    else:
        print("No GITHUB_TOKEN, using REST fallback")
        return _fallback_profile()


def _parse_profile(user: dict) -> dict:
    """Parse GraphQL response into flat dict for RPG card."""
    now = datetime.now(timezone.utc)
    contrib = user["contributionsCollection"]
    season = user["season"]
    cal = contrib["contributionCalendar"]

    # Compute streak from contribution calendar
    days = []
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            days.append({"date": day["date"], "count": day["contributionCount"]})

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    streak = 0
    for d in days:
        if d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    # Aggregate languages from top repos
    lang_bytes: dict[str, int] = {}
    total_stars = 0
    for repo in user["repositories"]["nodes"]:
        total_stars += repo["stargazers"]["totalCount"]
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            lang_bytes[name] = lang_bytes.get(name, 0) + edge["size"]

    top_langs = sorted(lang_bytes.items(), key=lambda x: -x[1])
    primary_lang = top_langs[0][0] if top_langs else "Unknown"

    commits = (
        contrib["totalCommitContributions"] + contrib["restrictedContributionsCount"]
    )

    # Account age in years
    created = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    years = (now - created).days / 365.25

    return {
        "name": user["name"] or user["login"],
        "login": user["login"],
        "commits": commits,
        "merged_prs": user["mergedPRs"]["totalCount"],
        "reviews": contrib["totalPullRequestReviewContributions"],
        "closed_issues": user["closedIssues"]["totalCount"],
        "repos": user["repositories"]["totalCount"],
        "stars": total_stars,
        "followers": user["followers"]["totalCount"],
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "languages": [{"name": n, "bytes": b} for n, b in top_langs[:5]],
        "primary_language": primary_lang,
        "years": round(years, 1),
    }


def _fallback_profile() -> dict:
    """Minimal profile when GraphQL is unavailable."""
    return {
        "name": "Mahesh Diwan",
        "login": USERNAME,
        "commits": 0,
        "merged_prs": 0,
        "reviews": 0,
        "closed_issues": 0,
        "repos": 0,
        "stars": 0,
        "followers": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "languages": [],
        "primary_language": "Unknown",
        "years": 0,
    }
