# First-Pass Repo Review

## When To Use

Use this before changing unfamiliar Scrape-n-Email code or when asked to summarize repo state.

## Inputs To Ask For

- Target bug, feature, PR, or file area.
- Whether live-site behavior or offline parser behavior is in scope.

## Workflow

1. Read `AGENTS.md`, `README.md`, and `CONTRIBUTING.md`.
2. Inspect `.github/workflows/ci.yml` for the test matrix.
3. Identify the owning file: scraper, `csv_helper.py`, `mailer.py`, or `main.py`.
4. Check existing tests in `test_scrapers.py` and `test_mailer_csv.py`.
5. Report what is already covered and what needs verification.

## Verification Checklist

- Root files and CI inspected.
- Existing generated artifacts identified and left alone.
- No edits made unless requested.

## Expected Final Response

- Scope inspected.
- Relevant files and tests.
- Risks or unknowns.
- Suggested next step.
