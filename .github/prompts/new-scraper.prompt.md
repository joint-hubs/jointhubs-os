---
agent: Tech Lead
tools: ['read', 'edit', 'search', 'web']
description: Create a new web scraper for a specific use case
---

# New Scraper

Create a scraper for a specific website or use case.

## Steps

1. **Get target URL from user** if not provided
2. **Take page snapshot** using browser tools
3. **Analyze structure**:
   - Find repeating elements (cards, rows, items)
   - Identify unique selectors for each field
   - Check for pagination
   - Note any anti-bot measures
4. **Create scraper file** in the project's scrapers directory
5. **Use base class** from `lib/base_scraper.py`
6. **Test with 5-10 items** before full run

## Output Structure

```python
# scrapers/{name}_scraper.py
from lib import BaseScraper, ScraperConfig

class {Name}Scraper(BaseScraper):
    def get_item_selector(self) -> str:
        return "{selector}"
    
    def extract_item(self, element) -> dict:
        return {
            "field1": self.safe_text(element, "{sel1}"),
            "field2": self.safe_attr(element, "{sel2}", "href"),
        }
```

## Skill Reference

If you keep a scraper skill locally, load it before implementation. Useful content includes:
- Selector priority hierarchy
- Pagination patterns
- Anti-bot solutions
- Debugging techniques

## Handoff

After creating scraper:
- **Run it** → Test locally
- **Deploy** → Hand off to Tech Lead for Apify
