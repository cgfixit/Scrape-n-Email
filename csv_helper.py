#!/usr/bin/env python3
"""
csv_helper.py — Shared CSV utilities for RCPlinks.csv

Extracted from drudgeScraper.py to eliminate circular imports and centralize
header management / formula-injection safety.

Used by:
- rcpScraper.scrape() — appends headlines during normal runs
- drudgeScraper standalone (__main__) — for testing / legacy Drudge flow

Functions are intentionally simple and side-effect heavy (file I/O) because
this is a small personal automation script, not a library.
"""

import csv
import os


def _csv_safe(value):
    """
    Neutralize CSV formula injection.
    Spreadsheet apps execute a cell whose first char is = + - @ (or leading tab/CR),
    so scraped, attacker-controlled text gets a leading apostrophe to force literal.
    """
    text = "" if value is None else str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def csvinit():
    """
    Initialize (or re-initialize) RCPlinks.csv with header row.
    Uses 'w' mode so we start clean. Called automatically by rcpScraper
    on first run or when file is missing/empty. Safe to call multiple times
    (idempotent in effect for our use case).
    Returns True on success, False on I/O failure.
    """
    try:
        with open('RCPlinks.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(('HEADLINE', 'URL'))
            # Keep a blank row for visual separation (legacy behavior)
            writer.writerow(('', ''))
        print("[csv_helper] Initialized RCPlinks.csv with header")
        return True
    except OSError as e:
        print(f"[csv_helper] Failed to initialize RCPlinks.csv: {e}")
        return False


def writer(title, link):
    """
    Append a single (title, link) row to RCPlinks.csv.
    Creates file if it doesn't exist (but header should have been ensured by caller).
    Returns True on success, False on I/O failure.
    """
    try:
        with open('RCPlinks.csv', 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow((_csv_safe(title), _csv_safe(link)))
        return True
    except OSError as e:
        print(f"[csv_helper] Failed to append to RCPlinks.csv: {e}")
        return False
