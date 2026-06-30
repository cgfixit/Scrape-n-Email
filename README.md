# Scrape-n-Email (Modernized Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/CGFixIT/Scrape-n-Email/actions/workflows/ci.yml/badge.svg)](https://github.com/CGFixIT/Scrape-n-Email/actions/workflows/ci.yml)

A small, dependency-light news + jobs scraper that emails its results as attachments.
This is the **fixed and cleaned-up version** of the original repo with the following improvements:

### Key Fixes Applied (June 2026)
- **Circular import eliminated**: CSV writing logic (`csvinit`, `writer`, `_csv_safe`) extracted to new `csv_helper.py`. `drudgeScraper.py` and `rcpScraper.py` now both import from it cleanly.
- **RCPlinks.csv header management**: `rcpScraper.scrape()` now auto-initializes the CSV with a proper header row on first run (or when file is missing/empty). No more missing headers or manual `csvinit()` calls in normal flow.
- **Windows-specific popup removed**: The fragile `os.system('msg * ...')` line is gone from `main.py`. Replaced with proper `logging` (cross-platform, cron-friendly, redirectable).
- **Code quality / hygiene**:
  - Added `encoding="utf-8"` to all file opens.
  - Cleaner imports, removed unused `io`/`sys`/`bs4`/`requests` from `main.py`.
  - `csv_helper.py` has docstrings and is self-contained.
  - `.gitignore` added for sane Python project defaults (ignores generated .txt/.csv by default).
- **Tests still pass**: `test_scrapers.py` exercises all `parse_*` functions offline. No behavior change to parsing logic.

### What it does (unchanged core behavior)

Three scraper modules feed one orchestrator and one mailer:

```
main.py
  ├── rcpScraper.scrape()           → RCPheadlines.txt + appends to RCPlinks.csv (via csv_helper)
  ├── clistScraper.scrape()         → jobs.txt
  └── mailer.send_all()
        ├── Email 1: "Daily News: <date>" → RCPheadlines.txt + RCPlinks.csv
        └── Email 2: "Daily Jobs: <date>" → jobs.txt
```

- `rcpScraper` pulls top headlines from RealClearPolitics and writes a flat `.txt` digest plus a parallel `.csv`.
- `clistScraper` pulls Atlanta Craigslist sysadmin job listings into a `.txt` digest.
- `drudgeScraper` still contains a fully functional Drudge Report scraper (standalone or future use) but is **not called from main.py** (legacy pivot to RCP focus). Its CSV helpers were moved out.
- `mailer` sends two separate emails via Gmail SMTP — one for news, one for jobs — with the corresponding files attached. Date-stamped subject lines. Pure stdlib, App Password only.

> **About the `drudgeScraper` module name:** kept for historical reasons and because the Drudge parsing logic is still useful/standalone. The CSV code that used to live here is now centralized in `csv_helper.py`.

### How I use it daily

This is a lightweight personal automation that runs on my Windows machine every morning.

- It triggers automatically at 7:00 AM via Windows Task Scheduler.
- I get two separate emails:
  - **Daily News** — Top RealClearPolitics headlines + a growing `RCPlinks.csv` archive of links.
  - **Daily Jobs** — Atlanta Craigslist sysadmin / ops / infrastructure listings.
- The jobs email lets me stay passively aware of the local market without manually checking Craigslist every day.
- The news digest gives a quick, curated view of political and current events from a site whose aggregation style I like.
- Over time the CSV becomes a simple personal searchable archive of interesting links.
- When sites change layout I update the scraper; the offline tests in `test_scrapers.py` usually surface regressions quickly.

It stays small and focused on my actual daily workflow rather than trying to be a general tool.

### Setup (same as before, plus new file)

**Requirements:** Python 3.10+, `requests`, `beautifulsoup4`.

```bash
pip install -r requirements.txt
```

**Tests:**

```bash
python -m unittest test_scrapers -v
```

**Credentials** via environment variables (never in repo):

| Variable         | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| `EMAIL_USER`     | Gmail address to send from                                              |
| `EMAIL_PASS`     | Gmail App Password (16-char token)                                      |
| `EMAIL_RECIPIENT`| (Optional) destination; defaults to `EMAIL_USER`                        |

**Running it:**

```bash
# one-off (set env vars first!)