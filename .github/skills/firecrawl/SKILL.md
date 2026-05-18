---
name: firecrawl
description: |
  Use Firecrawl for markdown-first web scraping, crawling, and site mapping.
  Use when: "firecrawl", "crawl docs", "scrape website to markdown", "map website", "rag crawl".
---

# Firecrawl Skill

Use Firecrawl when the goal is to turn public web pages into LLM-friendly content, especially markdown, without building custom selector logic.

## What Firecrawl Is Good For

- Crawling documentation sites into markdown
- Mapping a site's URL structure before a scrape
- Pulling article or docs content for RAG pipelines
- Fast content ingestion where DOM-perfect field extraction is not required

## What Firecrawl Is Not For

- Precise field extraction from repeated cards, tables, or listings
- Highly custom browser flows that require selector-by-selector control
- Sensitive or regulated data flows without separate legal review

For those cases, prefer the existing local scraper stack or a project-specific Playwright flow.

## Repo Entry Point

Firecrawl is wired into the Jointhubs scraper toolkit here:

- `Second Brain/Projects/jointhubs/projekty/scrapers/firecrawl_cli.py`
- `Second Brain/Projects/jointhubs/projekty/scrapers/firecrawl.md`

The CLI auto-loads `Second Brain/Projects/jointhubs/projekty/scrapers/.env` and reads `FIRECRAWL_API_KEY` from there if it is not already exported in the shell.

## Commands

### Scrape One Page

```powershell
Set-Location "Second Brain/Projects/jointhubs/projekty/scrapers"
python firecrawl_cli.py scrape https://firecrawl.dev --format markdown
```

### Crawl a Site

```powershell
Set-Location "Second Brain/Projects/jointhubs/projekty/scrapers"
python firecrawl_cli.py crawl https://firecrawl.dev --limit 20 --format markdown --format html
```

### Map a Site

```powershell
Set-Location "Second Brain/Projects/jointhubs/projekty/scrapers"
python firecrawl_cli.py map https://firecrawl.dev
```

## Environment Setup

```powershell
pip install firecrawl-py
```

Add to the scraper-local `.env` file:

```env
FIRECRAWL_API_KEY=fc-your-key
```

## Decision Rule

Use this tool choice:

| Need | Tool |
|------|------|
| Extract fields via selectors | `BaseScraper` |
| Use hosted scraping actors | Apify |
| Crawl docs/pages into markdown | Firecrawl |
| Discover URLs first | Firecrawl `map` |

## Output Convention

By default, outputs are written to:

```text
Second Brain/Projects/jointhubs/projekty/scrapers/output/firecrawl/
```

Results are timestamped JSON snapshots so they can be reused in downstream scripts.

## Caveat

Firecrawl is a remote service. Only use it for data you are comfortable sending to a third-party processor under their terms.

## Related Skills

- [agentic-engineering](../agentic-engineering/SKILL.md) — packaging repeatable agent workflows