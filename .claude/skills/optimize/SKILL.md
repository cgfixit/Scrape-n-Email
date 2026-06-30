---
name: optimize
description: Tighten a Scrape-n-Email hotspot or piece of bloat with a small, measurable improvement. Prefer deletion, reuse, and stdlib over new abstractions. Use when the task targets a known slow or wasteful spot — scraper parsing, CSV writes, SMTP retry, HTTP session reuse, or test-suite churn — and "make it faster/leaner without changing behavior" is the goal.
---

# Optimize

Read `CLAUDE.md` and `AGENTS.md` first.

Optimize this Scrape-n-Email change or hotspot. Keep scope tight.

## Fill in

- Goal:
- Current behavior:
- Bottleneck or bloat:
- Constraints:
- Tests:

## Bias

- Prefer deletion over addition.
- Prefer the stdlib and existing helpers over new dependencies.
- Prefer one measurable improvement over a sweep of stylistic edits.
- Reuse the shared HTTP session (`scrapers/base.get`) instead of opening
  new `requests.Session()` instances per call.
- Batch CSV writes through `scrape_n_email.csv` rather than re-opening
  `RCPlinks.csv` per row.
- Don't trade clarity for micro-gains in cold code paths (init, CLI parsing).

## State explicitly

- What was changed and why.
- What was **not** changed and why (so reviewers can see the bounded scope).
- How the improvement was measured (timing, allocation count, line count,
  coverage, CI wall-clock) — even a back-of-envelope number beats none.

## Verify before declaring done

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/scrape_n_email
pytest tests/ --cov=scrape_n_email --cov-report=term-missing --cov-fail-under=80
```

Coverage must stay above 80% (the CI gate). If a refactor removes a code
path, delete its tests in the same commit — don't leave them as dead
fixtures.
