#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from dateutil import parser as dateparser
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", default="data/news.json")
    parser.add_argument("--out", dest="outfile", default="index.html")
    parser.add_argument("--templates", default="templates")
    args = parser.parse_args()

    with open(args.infile) as f:
        payload = json.load(f)
    items = payload.get("items", [])

    # Group items by date (MM-DD-YYYY) based on published timestamp
    grouped = {}
    for it in items:
        pub = it.get("published")
        try:
            dt = dateparser.parse(pub)
        except Exception:
            dt = datetime.now(timezone.utc)
        key = dt.strftime("%m-%d-%Y")
        grouped.setdefault(key, []).append(it)

    env = Environment(
        loader=FileSystemLoader(args.templates),
        autoescape=select_autoescape(["html", "xml"]) 
    )
    tmpl = env.get_template("index.html.j2")
    generated_date = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    # Sort day sections descending
    day_sections = sorted(grouped.items(), key=lambda kv: datetime.strptime(kv[0], "%m-%d-%Y"), reverse=True)
    html = tmpl.render(items=items, day_sections=day_sections, generated_date=generated_date)

    with open(args.outfile, "w") as f:
        f.write(html)
    print(f"Wrote site to {args.outfile} with {len(items)} items")


if __name__ == "__main__":
    main()
