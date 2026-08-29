from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
import json
import os
import re

import requests
from bs4 import BeautifulSoup

USERNAME = os.getenv("Dev-Xrab", "Dev-Xrab")
OUTPUT = Path("data/contributions.json")

URL = f"https://github.com/users/{Dev-Xrab}/contributions"

def parse_count(text: str) -> int:
    text = text.replace(",", "")
    match = re.search(r"(\d+)\s+contribution", text, re.I)
    return int(match.group(1)) if match else 0

def fetch_days():
    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 GitHub-Profile-README-Updater",
            "Accept": "text/html",
        },
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    days = []

    # GitHub has changed the exact markup more than once. Support the
    # commonly observed attributes instead of coupling to one tag name.
    candidates = soup.select("[data-date]")

    for node in candidates:
        raw_date = node.get("data-date")
        if not raw_date:
            continue

        try:
            datetime.strptime(raw_date, "%Y-%m-%d")
        except ValueError:
            continue

        count = None

        # Older / alternate markup.
        if node.has_attr("data-count"):
            try:
                count = int(node["data-count"])
            except (TypeError, ValueError):
                pass

        # GitHub accessibility labels normally include "... contributions".
        if count is None:
            label = (
                node.get("aria-label")
                or node.get("data-tooltip")
                or node.get("title")
                or node.get_text(" ", strip=True)
            )
            count = parse_count(label)

        level = 0
        if node.has_attr("data-level"):
            try:
                level = int(node["data-level"])
            except (TypeError, ValueError):
                level = 0

        days.append({"date": raw_date, "count": count, "level": level})

    # De-duplicate by date because labels and visual cells can both carry data-date.
    unique = {}
    for day in days:
        previous = unique.get(day["date"])
        if previous is None or day["count"] > previous["count"]:
            unique[day["date"]] = day

    return sorted(unique.values(), key=lambda x: x["date"])

def streaks(days):
    by_date = {date.fromisoformat(d["date"]): d["count"] for d in days}
    if not by_date:
        return 0, 0

    first = min(by_date)
    last = max(by_date)

    longest = 0
    run = 0
    cursor = first

    while cursor <= last:
        if by_date.get(cursor, 0) > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
        cursor += timedelta(days=1)

    # Current streak ends at the latest represented day. If today has no
    # contribution yet, allow yesterday as the streak endpoint.
    endpoint = last
    if by_date.get(endpoint, 0) == 0:
        endpoint -= timedelta(days=1)

    current = 0
    cursor = endpoint
    while by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    return current, longest

def derive_stats(days):
    total = sum(d["count"] for d in days)
    current, longest = streaks(days)

    best = max(days, key=lambda d: d["count"], default=None)

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": dict(sorted(monthly.items())),
    }

def main():
    if USERNAME == "Dev-Xrab":
        raise SystemExit(
            "Replace Dev-Xrab in scripts/fetch_contributions.py "
            "or set Dev-Xrab."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    days = fetch_days()

    if not days:
        raise SystemExit(
            "No contribution cells were parsed. GitHub may have changed the "
            "public contributions HTML. Inspect the endpoint before changing selectors."
        )

    payload = {
        "username": Dev-Xrab,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "days": days,
        "stats": derive_stats(days),
    }

    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(days)} days)")

if __name__ == "__main__":
    main()
