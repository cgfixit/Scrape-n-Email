"""CLI entry point for scrape-n-email."""

from __future__ import annotations

import argparse
import logging
import sys

from scrape_n_email.config import Config
from scrape_n_email.csv import init_csv
from scrape_n_email.mailer import send_all
from scrape_n_email.scrapers import clist, drudge, rcp

logger = logging.getLogger("scrape_n_email")


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    """Run the daily scrape and email pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-email", action="store_true", help="scrape only")
    args = parser.parse_args(argv)

    setup_logging()
    config = Config.from_env()
    if not args.skip_email:
        try:
            config.validate()
        except ValueError as e:
            logger.error("Configuration error: %s", e)
            return 1

    logger.info("Starting daily scrape run...")
    init_csv(force=True)

    try:
        rcp.scrape()
    except Exception:
        logger.exception("RCP scraper failed")

    try:
        clist.scrape()
    except Exception:
        logger.exception("Craigslist scraper failed")

    if args.skip_email:
        return 0

    logger.info("Scraping complete. Sending emails...")
    try:
        send_all()
    except Exception:
        logger.exception("Email sending failed")
        return 1

    logger.info("All done.")
    return 0


def drudge_main(argv: list[str] | None = None) -> int:
    """Standalone Drudge scraper + RCP combo."""
    setup_logging()
    init_csv(force=True)
    drudge.scrape()
    rcp.scrape()
    return 0


if __name__ == "__main__":
    sys.exit(main())
