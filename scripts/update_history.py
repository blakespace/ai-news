#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--news", default="data/news.json")
    parser.add_argument("--notable", default="data/notable.json")
    parser.add_argument("--history", default="data/history")
    parser.add_argument("--date", default=None, help="ISO date YYYY-MM-DD; default uses current date in UTC")
    args = parser.parse_args()

    with open(args.news) as f:
        news_payload = json.load(f)
    with open(args.notable) as f:
        notable_payload = json.load(f)

    items = news_payload.get("items", [])
    notable = notable_payload.get("items", [])

    # Use provided date or current UTC date
    if args.date:
        day = args.date
    else:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    os.makedirs(args.history, exist_ok=True)
    path = os.path.join(args.history, f"{day}.json")

    record = {
        "date": day,
        "items": items,
        "notable": notable,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"Updated history: {path} (items={len(items)}, notable={len(notable)})")


if __name__ == "__main__":
    main()
