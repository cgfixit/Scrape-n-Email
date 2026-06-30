---
name: ponytail
description: Propose and apply the smallest, lazily-correct change to Scrape-n-Email. Reuse stdlib and existing helpers (scrapers/base.get, scrape_n_email.csv, the module logger) before reaching for new dependencies or abstractions. Use when the task is a focused bug fix, parser tweak, mailer adjustment, or any "just make this work" change where scope creep is the main risk.
---

# Ponytail

Read `CLAUDE.md` and `AGENTS.md` first.

Use the lazily correct solution:

- Ask whether this needs to exist at all.
- Reuse existing helpers first:
  - HTTP: `scrape_n_email.scrapers.base.get()` (shared session + retry).
  - CSV: `scrape_n_email.csv.append_row()` / `init_csv()` (formula-safe,
    non-truncating).
  - Logging: `logging.getLogger("scrape_n_email.<module>")` — never `print()`.
  - Config: `scrape_n_email.config.Config` for env-driven values.
- Avoid new dependencies. The runtime pins are `requests`, `beautifulsoup4`,
  `lxml`; the dev pins are `pytest`, `pytest-cov`, `ruff`, `mypy`,
  `python-dotenv`. Adding to either set needs a real reason.
- Avoid broad abstractions. Three similar lines beat a premature helper.
- Keep the diff as small as possible. Don't reformat adjacent code or
  rename unrelated symbols.
- Preserve generated-file contracts: `RCPheadlines.txt`, `jobs.txt`,
  `DRUDGEheadlines.txt`, `RCPlinks.csv`. Tests assert on their layout.

If the task is non-trivial, prefer the smallest working change and call out
any deliberate simplification with a `ponytail:` comment.

## Fill in

- Goal:
- Files:
- Constraints:
- Tests:

## Verify before declaring done

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/scrape_n_email
pytest tests/ -q
```
