# News Aggregator 📰
Scrapes top tech stories from Hacker News, Reddit r/programming, and Dev.to. 
Outputs a ranked feed sorted by engagement score.

## Features
- Multi-source scraping (HN, Reddit, Dev.to)
- Deduplication by title similarity
- Engagement scoring (upvotes + comments weighted)
- Export to JSON or Markdown digest
- Runs as daily cron or on-demand

## Usage
```bash
pip install -r requirements.txt
python aggregator.py --output digest.md
```

## Cron (daily digest)
```
0 8 * * * cd /path/to/news-aggregator && python aggregator.py >> daily.log
```
