"""CSV utilities for RCPlinks.csv with formula-injection protection."""

from __future__ import annotations

import csv
import logging
from collections.abc import Iterable
from pathlib import Path

logger = logging.getLogger("scrape_n_email.csv")

CSV_PATH = Path("RCPlinks.csv")


def _csv_safe(value: object | None) -> str:
    """Neutralize CSV formula injection."""
    text = "" if value is None else str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def init_csv(*, force: bool = False) -> bool:
    """Initialize RCPlinks.csv without truncating existing data unless forced."""
    if not force and CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
        logger.debug("CSV file already exists with data, skipping init")
        return False

    try:
        mode = "w" if force else "x"
        with CSV_PATH.open(mode, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(("HEADLINE", "URL"))
            writer.writerow(("", ""))
        logger.info("Initialized %s with header (force=%s)", CSV_PATH, force)
        return True
    except FileExistsError:
        logger.debug("CSV file already exists, skipping init")
        return False
    except OSError as e:
        logger.error("Failed to initialize %s: %s", CSV_PATH, e)
        return False


def append_row(title: str, link: str) -> bool:
    """Append a single (title, link) row to RCPlinks.csv."""
    try:
        with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow((_csv_safe(title), _csv_safe(link)))
        return True
    except OSError as e:
        logger.error("Failed to append to %s: %s", CSV_PATH, e)
        return False


def append_rows(rows: Iterable[tuple[str, str]]) -> bool:
    """Append multiple (title, link) rows to RCPlinks.csv in a single file open."""
    try:
        with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows((_csv_safe(title), _csv_safe(link)) for title, link in rows)
        return True
    except OSError as e:
        logger.error("Failed to append to %s: %s", CSV_PATH, e)
        return False
