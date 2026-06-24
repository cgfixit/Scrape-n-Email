#!/usr/bin/env python3
"""
main.py — Orchestrator for Scrape-n-Email

Calls the active scrapers (rcpScraper + clistScraper) then the mailer.
Drudge scraping logic remains available in drudgeScraper.py for standalone
use or future expansion (the module name is legacy from the original project).

Fixes applied in this version:
- Circular import eliminated by moving CSV logic to csv_helper.py
- RCPlinks.csv header is now auto-initialized on first run (or when empty)
- Windows-specific popup / msg command removed (unreliable cross-platform).
  Replaced with simple logging + success message. Add your own notification
  (e.g. plyer, notify-send, or Windows toast) if desired.
"""

import logging
import os

import rcpScraper
import clistScraper
import mailer

# Basic logging so we have timestamps and can easily redirect / cron it later.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    logging.info("Starting daily scrape run...")
    try:
        rcpScraper.scrape()
    except Exception as err:
        logging.error("RCP scraper raised an unexpected error: %s", err)
    try:
        clistScraper.scrape()
    except Exception as err:
        logging.error("Craigslist scraper raised an unexpected error: %s", err)
    logging.info("Scraping complete. Handing off to mailer...")


if __name__ == "__main__":
    main()
    mailer.send_all()
    logging.info("All done. Emails attempted. Check logs above for any SMTP issues.")
    # No more Windows-only os.system popup. This was fragile and non-portable.
    # If you want a desktop notification on Windows, consider:
    #   from plyer import notification
    #   notification.notify(title="Scrape-n-Email", message="Daily digest sent!")
