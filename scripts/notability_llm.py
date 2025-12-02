#!/usr/bin/env python3
import argparse
import json
import os
from typing import List, Dict
from openai import OpenAI
# OpenAI SDK (optional). If not available or no key, we fallback.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROMPT_SYSTEM =  """
You are an expert AI news curator focused on breakthrough releases in object detection, 
image classification, segmentation, and large language models (LLMs).
Assess each item for whether it is highly notable or groundbreaking for practitioners and researchers.
This should be for major advancements for broad models or techniques, not incremental updates.
This is not new functionalities added to existing products unless they represent significant leaps.
Consider first-party releases, major performance improvements (SOTA), new architectures, or widely impactful updates. 
Respond in a strict JSON array with objects containing: 
'decision' ('include'|'exclude'), 'reason', and 'summary' (1-2 sentences). Keep summaries concise and neutral."

Do not wrap the returned json in ```json ... ``` blocks.
"""

PROMPT_USER_TEMPLATE = (
    "Review the following items and decide which are notable. Only include if strongly justified.\n\n" 
    "Items:\n{items}\n\nCategories of interest: object detection, classification, segmentation, LLMs."
)




def run_llm(items: List[Dict]) -> List[Dict]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    compact_items = [
        {
            "title": it.get("title"),
            "source": it.get("source"),
            "summary": it.get("summary"),
            "link": it.get("link"),
            "published": it.get("published"),
            "categories": it.get("categories", [])
        } for it in items
    ]
    user_content = PROMPT_USER_TEMPLATE.format(items=json.dumps(compact_items, indent=2))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # lightweight, cost effective; replace if needed
        messages=[
            {"role": "system", "content": PROMPT_SYSTEM},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2,
    )
    text = resp.choices[0].message.content.strip()
    selected = []
    text:str = text.lstrip("```json").rstrip("```")
    decisions = json.loads(text)
    for d, it in zip(decisions, items):
        if isinstance(d, dict) and d.get("decision") == "include":
            selected.append({
                "title": it["title"],
                "link": it["link"],
                "source": it["source"],
                "published": it["published"],
                "categories": it.get("categories", []),
                "summary": d.get("summary") or it.get("summary", ""),
                "notability_reason": d.get("reason", "LLM decision"),
            })
    return selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", default="data/news.json")
    parser.add_argument("--out", dest="outfile", default="data/notable.json")
    args = parser.parse_args()

    with open(args.infile) as f:
        payload = json.load(f)
    items = payload.get("items", [])
    notable = run_llm(items)

    os.makedirs(os.path.dirname(args.outfile), exist_ok=True)
    out = {"items": notable}
    with open(args.outfile, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {len(notable)} notable items to {args.outfile}")


if __name__ == "__main__":
    main()
