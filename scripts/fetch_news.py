#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from dateutil import parser as dateparser
import feedparser
import re
from typing import List, Dict

from config import KEYWORDS, EXCLUDE_PHRASES, CATEGORIES
from sources import SOURCES


def normalize_text(s: str) -> str:
    return (s or "").lower()


def matches_keywords(title: str, summary: str) -> bool:
    t = normalize_text(title)
    s = normalize_text(summary)
    if any(p in t or p in s for p in EXCLUDE_PHRASES):
        return False
    return any(k in t or k in s for k in KEYWORDS)


def detect_categories(title: str, summary: str) -> List[str]:
    t = normalize_text(title)
    s = normalize_text(summary)
    cats = []
    for cat, keys in CATEGORIES.items():
        if any(k.lower() in t or k.lower() in s for k in keys):
            cats.append(cat)
    return cats


def parse_date(entry) -> datetime:
    # feedparser often gives 'published' or 'updated'
    for field in ("published", "updated"):
        if getattr(entry, field, None):
            try:
                return dateparser.parse(getattr(entry, field)).astimezone(timezone.utc)
            except Exception:
                pass
    # fallback to now
    return datetime.now(timezone.utc)


def fetch_all(today_only: bool = True, window_hours: int | None = None) -> List[Dict]:
    items = []
    now = datetime.now(timezone.utc)
    for src in SOURCES:
        if src["type"] != "rss":
            continue
        fp = feedparser.parse(src["url"])  # network call
        for e in fp.entries:
            title = e.get("title", "")
            link = e.get("link", "")
            summary = e.get("summary", e.get("description", ""))
            dt = parse_date(e)
            if today_only or window_hours:
                # Consider items within provided window (default 24h)
                delta = now - dt
                max_seconds = (window_hours or 24) * 3600
                if delta.total_seconds() > max_seconds:
                    continue
            if not matches_keywords(title, summary):
                continue
            cats = detect_categories(title, summary)
            items.append({
                "source": src["name"],
                "title": title,
                "link": link,
                "summary": re.sub(r"<[^>]+>", "", summary).strip(),
                "published": dt.isoformat(),
                "categories": cats or ["general"],
            })
    # sort newest first
    items.sort(key=lambda x: x["published"], reverse=True)
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="today", help="Scope for fetch: today|all")
    parser.add_argument("--hours", type=int, default=None, help="Window in hours to include items (overrides --date today window)")
    parser.add_argument("--days", type=int, default=None, help="Window in days to include items")
    parser.add_argument("--out", default="data/news.json", help="Output JSON file path")
    args = parser.parse_args()

    window_hours = args.hours
    if args.days:
        window_hours = (args.days * 24)

    items = fetch_all(today_only=(args.date == "today" and window_hours is None), window_hours=window_hours)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "items": items}

    # ensure parent dir exists
    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {len(items)} items to {args.out}")


if __name__ == "__main__":
    main()
