Read `CLAUDE.md` and `AGENTS.md` first.

Use the lazily correct solution for this Scrape-n-Email task. Keep the smallest working diff.

- Ask whether this needs to exist at all.
- Reuse existing helpers: HTTP via `scrapers/base.get()`, CSV via `scrape_n_email.csv.append_row()` / `init_csv()`, logging via `logging.getLogger("scrape_n_email.<module>")`, config via `Config`.
- Avoid new dependencies. Runtime pins: `requests`, `beautifulsoup4`, `lxml`. Dev pins: `pytest`, `pytest-cov`, `ruff`, `mypy`, `python-dotenv`.
- Avoid broad abstractions — three similar lines beat a premature helper.
- Don't reformat adjacent code or rename unrelated symbols.
- Preserve generated-file contracts: `RCPheadlines.txt`, `jobs.txt`, `DRUDGEheadlines.txt`, `RCPlinks.csv`.
- Preserve offline tests, CSV formula-injection safety, and SMTP secret handling.

Mark deliberate simplifications with a `ponytail:` comment when useful.

Verify before declaring done:

```
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/scrape_n_email
pytest tests/ -q
```

Task: $ARGUMENTS
