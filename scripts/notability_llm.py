#!/usr/bin/env python3
import argparse
import json
import os
from typing import List, Dict

# OpenAI SDK (optional). If not available or no key, we fallback.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROMPT_SYSTEM = (
    "You are an expert AI news curator focused on breakthrough releases in object detection, image classification, segmentation, and large language models (LLMs). "
    "Assess each item for whether it is highly notable or groundbreaking for practitioners and researchers. Consider first-party releases, major performance improvements (SOTA), new architectures, or widely impactful updates. Respond in a strict JSON array with objects containing: 'decision' ('include'|'exclude'), 'reason', and 'summary' (1-2 sentences). Keep summaries concise and neutral."
)

PROMPT_USER_TEMPLATE = (
    "Review the following items and decide which are notable. Only include if strongly justified.\n\n" 
    "Items:\n{items}\n\nCategories of interest: object detection, classification, segmentation, LLMs."
)


def heuristic_filter(items: List[Dict]) -> List[Dict]:
    notable = []
    strong_terms = [
        "state-of-the-art", "SOTA", "outperforms", "new architecture", "release",
        "launch", "v1", "v2", "v3", "GPT", "Llama", "YOLO", "SAM", "ViT",
        "benchmark", "record", "breakthrough", "significant", "major", "open source",
    ]
    for it in items:
        text = f"{it.get('title','')} {it.get('summary','')}".lower()
        score = sum(t.lower() in text for t in strong_terms)
        # prefer first-party sources
        source_bonus = 1 if any(x in (it.get('source','')) for x in ["OpenAI", "Google", "Meta", "Anthropic", "Hugging Face"]) else 0
        if score + source_bonus >= 2:
            notable.append({
                "title": it["title"],
                "link": it["link"],
                "source": it["source"],
                "published": it["published"],
                "categories": it.get("categories", []),
                "summary": it.get("summary", ""),
                "notability_reason": "Heuristic strong-terms/source match",
            })
    return notable


def run_llm(items: List[Dict]) -> List[Dict]:
    try:
        from openai import OpenAI
    except Exception:
        return heuristic_filter(items)
    if not OPENAI_API_KEY:
        return heuristic_filter(items)

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
    try:
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
    except Exception:
        # fallback if LLM failed to produce parseable JSON
        selected = heuristic_filter(items)
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
