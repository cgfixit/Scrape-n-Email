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

### How you can use this:

This is a lightweight personal automation that runs on a Windows (or Linux with minor tweaks) machine ad hoc or via cron/task scheduler.

- It (hypothetically) triggers automatically at 7:00 AM via Windows Task Scheduler.
- You get two separate emails:
  - **Daily News** — Top RealClearPolitics headlines + a growing `RCPlinks.csv` archive of links.
  - **Daily Jobs** — Atlanta Craigslist sysadmin / ops / infrastructure listings.
- The news digest gives a quick, curated view of political and current events from a site whose aggregation style I like.
- Over time the CSV becomes a simple personal searchable archive of interesting links.
- When sites change layout code needs updates to the scraper; the offline tests in `test_scrapers.py` usually surface regressions quickly.

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
python main.py

# scheduled (Windows example)
schtasks /Create /SC DAILY /TN "ScrapeNEmail" /TR "C:\\path\\to\\python.exe C:\\path\\to\\main.py" /ST 07:00
```

### File Overview (Fixed Version)

| File                | Purpose                                                                 | Changed? |
|---------------------|-------------------------------------------------------------------------|----------|
| `csv_helper.py`     | New. CSV header init + safe append writer. No circular deps.            | **NEW**  |
| `clistScraper.py`   | Atlanta Craigslist sysadmin jobs (`/search/sad`)                        | Minor (encoding) |
| `drudgeScraper.py`  | Drudge Report parser + legacy standalone runner (now uses csv_helper)   | Yes (imports + calls) |
| `rcpScraper.py`     | RealClearPolitics headlines + auto CSV header + uses csv_helper         | Yes (init logic + import) |
| `main.py`           | Orchestrator (rcp + clist → mailer). Clean logging, no Windows popup.   | Yes      |
| `mailer.py`         | Gmail SMTP + attachments (pure stdlib)                                  | No       |
| `test_scrapers.py`  | Offline unit tests for all parse_* functions                            | No (still passes) |
| `requirements.txt`  | requests + beautifulsoup4                                               | Minor    |
| `.gitignore`        | Python + generated file hygiene                                         | **NEW**  |
| `README.md`         | This file                                                               | Updated  |

### Remaining Caveats (honest)

- Live scraping still depends on the sites not changing their HTML too aggressively and your egress IP not being blocked. The robust headers + retries + fallbacks help a lot.
- `RCPlinks.csv` now grows over time (append-only design). If you want daily rotation or size limits, add a small cleanup step in `main.py` or `rcpScraper.scrape()`.
- Drudge scraping is present but dormant in the daily `main.py` flow. If you want headlines from Drudge in the email too, add `import drudgeScraper; drudgeScraper.scrape()` in `main()` and update the mailer to attach `DRUDGEheadlines.txt`.

### Why these fixes matter

The original had classic small-project tech debt:
- Circular imports (fragile on reload / certain Python versions)
- First-run CSV without header (silent data quality issue)
- Non-portable "success popup" that only worked on one dev's Windows box

---

*Christopher Grady · @cgfixit · cgfixit.com · June 2026 (fixed edition)*

Original repo: https://github.com/CGFixIT/Scrape-n-Email
