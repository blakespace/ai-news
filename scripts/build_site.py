#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", default="data/notable.json")
    parser.add_argument("--out", dest="outfile", default="index.html")
    parser.add_argument("--templates", default="templates")
    args = parser.parse_args()

    with open(args.infile) as f:
        payload = json.load(f)
    items = payload.get("items", [])

    env = Environment(
        loader=FileSystemLoader(args.templates),
        autoescape=select_autoescape(["html", "xml"]) 
    )
    tmpl = env.get_template("index.html.j2")
    generated_date = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    html = tmpl.render(items=items, generated_date=generated_date)

    with open(args.outfile, "w") as f:
        f.write(html)
    print(f"Wrote site to {args.outfile} with {len(items)} items")


if __name__ == "__main__":
    main()
