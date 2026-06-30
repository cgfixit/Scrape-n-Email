Read `CLAUDE.md` and `AGENTS.md` first.

Optimize this Scrape-n-Email hotspot or piece of bloat with a small, measurable improvement. Keep scope tight.

Bias:
- Prefer deletion over addition.
- Prefer the stdlib and existing helpers over new dependencies.
- Prefer one measurable improvement over a sweep of stylistic edits.
- Reuse the shared HTTP session (`scrapers/base.get`) instead of opening new `requests.Session()` instances per call.
- Batch CSV writes through `scrape_n_email.csv` rather than re-opening `RCPlinks.csv` per row.
- Don't trade clarity for micro-gains in cold code paths (init, CLI parsing).

State explicitly:
- What was changed and why.
- What was **not** changed and why.
- How the improvement was measured (timing, line count, coverage, CI wall-clock).

Verify before declaring done:

```
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/scrape_n_email
pytest tests/ --cov=scrape_n_email --cov-report=term-missing --cov-fail-under=80
```

Coverage must stay above 80%. If a refactor removes a code path, delete its tests in the same commit.

Task: $ARGUMENTS
