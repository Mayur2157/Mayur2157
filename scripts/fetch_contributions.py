#!/usr/bin/env python3
"""
Scrapes Mayur's public contribution calendar from GitHub — no token needed.
Writes data/contributions.json with raw day data + derived stats.

Usage:
  python scripts/fetch_contributions.py
  USERNAME=Mayur2157 python scripts/fetch_contributions.py
"""
import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("USERNAME", "Mayur2157")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch() -> None:
    headers = {"User-Agent": "Mozilla/5.0 (profile-art-bot/1.0; +github.com/Mayur2157)"}
    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # ── Step 1: parse contribution counts from tooltip text nodes ─────────────
    # GitHub embeds "N contributions on Month Dayth." as visible text in <tool-tip>
    # elements or adjacent text. We parse them into a date→count map.
    count_map: dict[str, int] = {}

    MONTHS_FULL = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12,
    }
    # Match: "3 contributions on December 2nd." or "1 contribution on June 29th."
    tip_pat = re.compile(
        r"(\d+)\s+contributions?\s+on\s+(\w+)\s+(\d+)\w*",
        re.IGNORECASE,
    )

    for text_node in soup.find_all(string=True):
        m = tip_pat.search(text_node.strip())
        if m:
            count_raw, month_name, day_raw = m.group(1), m.group(2), m.group(3)
            month_num = MONTHS_FULL.get(month_name.capitalize())
            if month_num is None:
                continue
            # Determine year: use the cell's data-date as ground truth when available
            count_map[f"{month_name.capitalize()}-{int(day_raw)}"] = int(count_raw)

    # ── Step 2: parse grid cells ───────────────────────────────────────────────
    days: list[dict] = []
    for td in soup.select("td.ContributionCalendar-day, td[data-date]"):
        date_str = td.get("data-date")
        if not date_str:
            continue
        level = int(td.get("data-level", 0))

        # Resolve count: from tooltip text, matched by month+day since we lack year
        # (GitHub only shows the year in the full profile page, not the fragment)
        dt = date.fromisoformat(date_str)
        month_name = dt.strftime("%B")
        key = f"{month_name}-{dt.day}"
        count = count_map.get(key, 0)

        days.append({"date": date_str, "level": level, "count": count})

    if not days:
        raise RuntimeError(
            "No contribution data found — GitHub may have changed its HTML structure."
        )

    # ── Step 3: scrape total from the "N contributions in the last year" heading ──
    total_scraped = 0
    total_pat = re.compile(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", re.IGNORECASE)
    for text_node in soup.find_all(string=True):
        m = total_pat.search(text_node.strip())
        if m:
            total_scraped = int(m.group(1).replace(",", ""))
            break
    total = total_scraped if total_scraped else sum(d["count"] for d in days)

    # ── Step 4: derived stats ─────────────────────────────────────────────────
    sorted_days = sorted(days, key=lambda d: d["date"])
    today_str = date.today().isoformat()

    # Current streak (backwards from today)
    current_streak = 0
    for d in reversed(sorted_days):
        if d["date"] > today_str:
            continue
        if d["count"] > 0 or d["level"] > 0:
            current_streak += 1
        else:
            break

    # Longest streak (forward pass)
    longest_streak = 0
    run = 0
    for d in sorted_days:
        if d["count"] > 0 or d["level"] > 0:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 0

    best = max(days, key=lambda d: d["count"]) if days else {}
    monthly: dict[str, int] = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    result = {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best,
        "monthly_totals": dict(sorted(monthly.items())),
        "days": days,
    }

    os.makedirs("data", exist_ok=True)
    out = "data/contributions.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(
        f"[OK] Fetched {len(days)} days | {total:,} total contributions"
        f" | {current_streak}d current streak | {longest_streak}d best -> {out}"
    )


if __name__ == "__main__":
    fetch()
