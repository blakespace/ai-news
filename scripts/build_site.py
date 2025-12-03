#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from dateutil import parser as dateparser
import os
import glob
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", default="data/news.json")
    parser.add_argument("--out", dest="outfile", default="index.html")
    parser.add_argument("--templates", default="templates")
    parser.add_argument("--history", default="data/history", help="Directory of per-day JSON records")
    parser.add_argument("--days", type=int, default=7, help="Number of past days to render")
    args = parser.parse_args()

    # Load last N days from history directory
    day_sections = []
    if os.path.isdir(args.history):
        files = sorted(glob.glob(os.path.join(args.history, "*.json")))
        files.sort(reverse=True)
        for fp in files[:args.days]:
            try:
                with open(fp) as f:
                    rec = json.load(f)
                day_iso = rec.get("date")
                day_label = datetime.strptime(day_iso, "%Y-%m-%d").strftime("%m-%d-%Y") if day_iso else ""
                day_sections.append((day_label, rec.get("items", []), rec.get("notable", [])))
            except Exception:
                pass

    env = Environment(
        loader=FileSystemLoader(args.templates),
        autoescape=select_autoescape(["html", "xml"]) 
    )
    tmpl = env.get_template("index.html.j2")
    generated_date = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = tmpl.render(day_sections=day_sections, generated_date=generated_date)

    with open(args.outfile, "w") as f:
        f.write(html)
    total = sum(len(entries) for _, entries, _ in day_sections)
    print(f"Wrote site to {args.outfile} with {total} items across {len(day_sections)} days")


if __name__ == "__main__":
    main()
