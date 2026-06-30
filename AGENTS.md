# AGENTS.md

Guidance for Codex and other AI coding agents working in Scrape-n-Email. Read this before editing, then consult the canonical project docs instead of duplicating them.

Canonical references:

- `README.md` for project overview, setup, runtime behavior, and caveats.
- `CONTRIBUTING.md` for contributor workflow, style, tests, and PR expectations.
- `.github/workflows/ci.yml` for the exact CI test matrix.
- `.codex/README.md` for Codex routines, prompts, and checklists.
- `commands/` for repo-local Codex slash commands.

## Project Overview

Scrape-n-Email is a small Python automation that scrapes RealClearPolitics headlines and Atlanta Craigslist sysadmin job listings, writes text/CSV outputs, and emails daily digests through Gmail SMTP. It is intentionally dependency-light and built for personal scheduled use, especially Windows Task Scheduler.

The repo has been modernized to remove circular imports, centralize CSV writing in `csv_helper.py`, add robust offline parser tests, and replace Windows popup behavior with logging.

## Tech Stack Detected

- Language/runtime: Python. CI tests Python 3.10, 3.11, 3.12, and 3.13 on Ubuntu and Windows.
- Dependencies: `requests`, `beautifulsoup4`, `lxml`.
- Tests: standard-library `unittest`; no pytest config detected.
- CI: GitHub Actions in `.github/workflows/ci.yml`.
- Packaging/build: no `pyproject.toml`, `setup.py`, package lockfile, Makefile, justfile, Dockerfile, or devcontainer detected.
- AI/tooling instructions: Codex setup lives in `AGENTS.md`, `.codex/`, and `commands/`; routines and checklists are listed in `.codex/README.md`.

## Repository Layout

- `main.py` - orchestrates RCP scrape, Craigslist scrape, then email sending.
- `rcpScraper.py` - RealClearPolitics headline scraping, `RCPheadlines.txt`, and `RCPlinks.csv` append flow.
- `clistScraper.py` - Craigslist Atlanta sysadmin/networking job scraping into `jobs.txt`.
- `drudgeScraper.py` - legacy/standalone Drudge scraper, not called from `main.py`.
- `csv_helper.py` - CSV header initialization, append helper, and formula-injection escaping.
- `mailer.py` - Gmail SMTP email sending with attachments.
- `test_scrapers.py` - offline parser tests for scraper modules.
- `test_mailer_csv.py` - offline tests for CSV helper and mailer behavior.
- `.github/workflows/ci.yml` - CI matrix and import check.
- Generated runtime files: `jobs.txt`, `RCPheadlines.txt`, and `RCPlinks.csv`.

## Setup Commands

Use a virtual environment when working locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows activation:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

CI additionally installs `lxml`, but `requirements.txt` already includes it:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt lxml
```

## Run Commands

One-off run, after setting email environment variables:

```bash
python main.py
```

Windows scheduled-run example from the README:

```cmd
schtasks /Create /SC DAILY /TN "ScrapeNEmail" /TR "C:\path\to\python.exe C:\path\to\main.py" /ST 07:00
```

Standalone scraper modules can be run directly for focused manual checks:

```bash
python rcpScraper.py
python clistScraper.py
python drudgeScraper.py
```

## Test Commands

Primary offline parser tests from the README and CONTRIBUTING:

```bash
python -m unittest test_scrapers -v
```

CSV and mailer tests:

```bash
python -m unittest test_mailer_csv -v
```

Full CI-equivalent offline test discovery:

```bash
python -m unittest discover -v -p "test_*.py"
python -c "import main; print('main.py imports successfully')"
```

## Lint, Format, And Typecheck Commands

No formatter, linter, or typechecker configuration was detected. Do not invent a project lint gate. If adding one, update docs and CI intentionally.

## Safe Development Workflow

1. Read `README.md`, `CONTRIBUTING.md`, and this file.
2. Keep changes small and aligned with the personal-automation scope.
3. For parser changes, update or add offline HTML fixtures and parser tests.
4. For mailer changes, mock SMTP and avoid sending real email in tests.
5. Run `python -m unittest discover -v -p "test_*.py"` before finishing behavior changes.
6. Run `python -c "import main; print('main.py imports successfully')"` when import boundaries change.
7. Report any live-scrape behavior as manually verified only if you actually ran it against the real sites.

## Coding Conventions

- Keep parser functions pure where possible so they can be tested offline.
- Keep dependency count low; this is a small script, not a framework.
- Prefer explicit, readable code over clever one-liners.
- Use `logging` for orchestration/runtime status and avoid Windows-only notification code in cross-platform paths.
- Keep CSV logic centralized in `csv_helper.py`.
- Preserve existing module boundaries unless a focused refactor requires otherwise.

## Testing Expectations

- Do not add tests that require network access for ordinary CI.
- For scraping bugs, add a small representative HTML fixture to the relevant unittest file.
- For email behavior, mock `smtplib.SMTP` and use temporary files/directories.
- For generated output files, prefer temp directories in tests and avoid relying on committed runtime artifacts.

## Dependency Management Rules

- Keep `requirements.txt` as the single dependency manifest unless the project intentionally adopts packaging metadata.
- Do not add dependencies for small conveniences.
- If scraper behavior requires parser changes, prefer BeautifulSoup/lxml patterns already in use.
- If adding a dependency, update README/CONTRIBUTING and CI install expectations.

## Security And Secrets Rules

- Never commit Gmail credentials, app passwords, `.env` files, or local scheduler paths.
- Required runtime environment variables:
  - `EMAIL_USER`
  - `EMAIL_PASS`
  - optional `EMAIL_RECIPIENT`
- Treat scraped site content as untrusted input.
- Preserve `csv_helper._csv_safe()` behavior; spreadsheet formula injection is a real risk for generated CSVs.
- Do not run live email sends as a test unless the maintainer explicitly asks.

## GitHub, Codex, And PR Permissions

- GitHub connector repo metadata reported admin/maintain/pull/push/triage access during this setup pass.
- Connector installation/list APIs returned empty results in this environment. If connector writes or PR comments fail with `Resource not accessible by integration`, update the GitHub App/connector installation permissions outside the repo.
- Local `gh` was not installed in the setup environment. Install and authenticate it before relying on `gh`-based workflows.
- CI workflow permissions are separate from connector permissions. `.github/workflows/ci.yml` does not declare an explicit `permissions:` block because it only needs checkout, dependency install, tests, and import verification.

## Git Workflow Expectations

- Prefer feature branches and PRs for behavior changes.
- Keep docs-only setup changes separate from scraper or mailer behavior changes.
- Do not force-push without explicit maintainer approval.
- Include tests run and any live-site/manual verification in PR descriptions.

## PR And Review Expectations

- For parser changes, explain the site/layout behavior being handled and include an offline fixture.
- For mailer changes, explain credential/env var impact and confirm SMTP is mocked in tests.
- For generated files, confirm `jobs.txt`, `RCPheadlines.txt`, and `RCPlinks.csv` are not committed.
- For dependency changes, explain why the dependency is worth the added maintenance surface.

## Known Gotchas

- Live scraping can break when RCP or Craigslist changes HTML or blocks the request.
- Offline tests validate parser logic, not current live-site selectors.
- `drudgeScraper.py` is available but dormant in the normal `main.py` flow.
- `RCPlinks.csv` is append-only by design and can grow over time.
- `jobs.txt`, `RCPheadlines.txt`, and `RCPlinks.csv` are runtime artifacts and ignored.
- Gmail requires an app password, not the account password.
- The README contains historical Windows scheduling details; avoid replacing them unless changing that workflow.

## Do Not

- Do not commit secrets, `.env`, scheduler machine paths, or generated scrape outputs.
- Do not make tests depend on network, Gmail, or live websites.
- Do not broaden this into a general scraping framework without maintainer approval.
- Do not remove CSV formula-injection escaping.
- Do not replace existing simple unittest flow with heavier tooling without a clear reason.
