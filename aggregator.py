#!/usr/bin/env python3
"""Multi-source tech news aggregator."""

import argparse
import time
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()
HEADERS = {"User-Agent": "news-aggregator/1.0"}

def fetch_hackernews(limit=30):
    stories = []
    try:
        ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).json()[:limit]
        for story_id in ids[:limit]:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5).json()
            if item and item.get("type") == "story":
                stories.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                    "source": "Hacker News",
                })
            time.sleep(0.05)
    except Exception as e:
        console.print(f"[red]HN error: {e}[/red]")
    return stories

def fetch_reddit_programming(limit=25):
    stories = []
    try:
        r = requests.get("https://www.reddit.com/r/programming/top.json?limit=25&t=day", headers=HEADERS, timeout=10)
        for post in r.json()["data"]["children"]:
            p = post["data"]
            stories.append({
                "title": p["title"],
                "url": p.get("url", ""),
                "score": p["score"],
                "comments": p["num_comments"],
                "source": "Reddit r/programming",
            })
    except Exception as e:
        console.print(f"[red]Reddit error: {e}[/red]")
    return stories

def fetch_devto(limit=20):
    stories = []
    try:
        r = requests.get("https://dev.to/api/articles?top=1&per_page=20", timeout=10)
        for a in r.json():
            stories.append({
                "title": a["title"],
                "url": a["url"],
                "score": a.get("positive_reactions_count", 0),
                "comments": a.get("comments_count", 0),
                "source": "Dev.to",
            })
    except Exception as e:
        console.print(f"[red]Dev.to error: {e}[/red]")
    return stories

def rank_stories(stories):
    for s in stories:
        s["engagement"] = s["score"] + (s["comments"] * 3)
    return sorted(stories, key=lambda x: x["engagement"], reverse=True)

def deduplicate(stories):
    seen = set()
    unique = []
    for s in stories:
        key = s["title"][:40].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique

def to_markdown(stories, output_file):
    date = datetime.now().strftime("%Y-%m-%d")
    lines = [f"# Tech News Digest — {date}\n"]
    for i, s in enumerate(stories[:20], 1):
        lines.append(f"{i}. **[{s['title']}]({s['url']})** — {s['source']} | ⬆ {s['score']} | 💬 {s['comments']}")
    with open(output_file, "w") as f:
        f.write("\n".join(lines))
    console.print(f"[green]Digest saved to {output_file}[/green]")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="digest.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    console.print("[cyan]Fetching from Hacker News...[/cyan]")
    hn = fetch_hackernews()
    console.print("[cyan]Fetching from Reddit...[/cyan]")
    reddit = fetch_reddit_programming()
    console.print("[cyan]Fetching from Dev.to...[/cyan]")
    devto = fetch_devto()

    all_stories = deduplicate(rank_stories(hn + reddit + devto))

    table = Table(title="Top Stories Today")
    table.add_column("#", style="yellow", width=3)
    table.add_column("Title", style="white", max_width=55)
    table.add_column("Source", style="cyan")
    table.add_column("Score", style="green")
    for i, s in enumerate(all_stories[:10], 1):
        table.add_row(str(i), s["title"][:55], s["source"], str(s["engagement"]))
    console.print(table)

    if args.json:
        with open("digest.json", "w") as f:
            json.dump(all_stories, f, indent=2)
    else:
        to_markdown(all_stories, args.output)

if __name__ == "__main__":
    main()
