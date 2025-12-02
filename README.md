# AI News (Object Detection, Classification, Segmentation, LLMs)

A lightweight, daily-updated news feed focused on major AI model releases and breakthroughs in:
- Object Detection
- Image Classification
- Segmentation
- Large Language Models (LLMs)

The site is published via GitHub Pages and automatically refreshed every day at 8:00 AM Eastern.

## How it works
- A GitHub Actions workflow runs daily and executes small Python scripts to fetch news from curated RSS/API sources.
- Items are filtered by relevant keywords and categories.
- The static site (`index.html`) is rebuilt. If no qualifying news is found, the homepage shows "No updates today" for a clean experience.

## Local development

### Prerequisites
- Python 3.10+

### Setup
```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_news.py --date today --out data/news.json
python scripts/build_site.py --in data/news.json --out index.html
```

### Preview
Open `index.html` in a browser.

## Deployment
- Enabled via GitHub Pages. The workflow handles building and publishing.

## Configuration
- Keyword tuning: `scripts/config.py`
- Sources: `scripts/sources.py`
- Template: `templates/index.html.j2`

## Notes
- This project avoids posting filler; if there are no relevant updates, the page shows a simple notice.
