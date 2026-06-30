# CLAUDE.md

Guidance for Claude Code working in Scrape-n-Email. Read this before editing.
Repo-wide guidance for any AI agent lives in `AGENTS.md`; this file adds the
Claude Code specifics (skills, slash commands, and the src-layout package
introduced by the modernization PR).

## Project at a Glance

Scrape-n-Email scrapes RealClearPolitics headlines, Atlanta Craigslist
sysadmin jobs, and (standalone) Drudge headlines, then emails a daily digest
through Gmail SMTP. It is dependency-light and built for scheduled personal
use.

## Layout (src-layout package)

- `src/scrape_n_email/` - installable package
  - `cli.py`, `__main__.py` - `python -m scrape_n_email` entry point
  - `config.py` - `Config` dataclass loaded from env vars
  - `csv.py` - CSV init, append, and formula-injection escaping
  - `mailer.py` - Gmail SMTP with retry + structured logging
  - `scrapers/base.py` - shared `requests.Session` + retry adapter
  - `scrapers/rcp.py`, `scrapers/clist.py`, `scrapers/drudge.py` - parsers
- `tests/unit/`, `tests/integration/` - pytest suite
- `pyproject.toml` - build, deps, ruff, mypy, pytest config
- `.github/workflows/ci.yml` - lint (ruff + mypy) + test matrix
- `.codex/` - Codex prompts/routines/checklists (Claude mirrors live in `.claude/`)

Generated runtime files: `jobs.txt`, `RCPheadlines.txt`, `DRUDGEheadlines.txt`,
`RCPlinks.csv`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate            # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run

```bash
python -m scrape_n_email             # full pipeline (needs email env vars)
```

## Verify a Change

The CI matrix is the source of truth (`.github/workflows/ci.yml`). Locally
match it before pushing:

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/scrape_n_email
pytest tests/ --cov=scrape_n_email --cov-report=term-missing --cov-fail-under=80
```

CI tests Python 3.10-3.13 on `ubuntu-latest` and `windows-2022`. Coverage gate
is 80%.

## Email Env Vars

`mailer.py` and `Config` read these. Never commit real values.

- `EMAIL_USER`, `EMAIL_PASS` (Gmail app password)
- `EMAIL_TO` (comma-separated recipients)
- Optional: `EMAIL_SUBJECT`, `EMAIL_HOST`, `EMAIL_PORT`

## Claude Code Skills

Skills tailored to this repo live in `.claude/skills/`:

- `ponytail` - propose the smallest, dependency-light change that satisfies
  the task. Reuse stdlib + existing helpers. Avoid new abstractions.
- `optimize` - tighten a hotspot (parser, CSV write, SMTP, HTTP session) with
  a small, measurable improvement. Prefer deletion, reuse, and stdlib over
  new dependencies.

Invoke with `/ponytail` or `/optimize`. The skill files mirror the Codex
prompt templates in `.codex/prompts/` so the two agents stay aligned.

## House Rules for Edits

- Keep the diff minimal. Don't refactor adjacent code on a bug-fix task.
- Reuse `scrapers/base.get()` for HTTP — don't create a new `Session`.
- Run CSV writes through `scrape_n_email.csv` so formula-injection escaping
  and append-not-truncate semantics are preserved.
- Never `print()` from library code; use the module logger.
- Tests are offline. Mock `requests`, file IO, and SMTP — do not make live
  network or SMTP calls.
- If you touch CI or `pyproject.toml`, re-run the four CI commands above.
