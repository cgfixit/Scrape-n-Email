"""Drudge Report headline scraper."""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from scrape_n_email.csv import append_row
from scrape_n_email.scrapers.base import get

logger = logging.getLogger("scrape_n_email.scrapers.drudge")

URL = "https://www.drudgereport.com/"
MAX_ITEMS = 60

_SKIP_HOSTS = (
    "drudgereport.com",
    "drudgereportarchives.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "t.me",
    "truthsocial.com",
    "googlesyndication.com",
    "doubleclick.net",
    "google.com",
)
_SKIP_PATH_SEGMENTS = {"privacy", "about", "contact", "rss", "advertise", "subscribe", "terms"}


def _is_headline_link(href: str, text: str) -> bool:
    if not href or not href.startswith("http"):
        return False
    parsed = urlparse(href.lower())
    host = parsed.netloc
    if any(host == h or host.endswith("." + h) for h in _SKIP_HOSTS):
        return False
    segments = [s for s in parsed.path.split("/") if s]
    if any(seg in _SKIP_PATH_SEGMENTS for seg in segments):
        return False
    return len(text) >= 12


def _is_emphasized(a: Tag) -> bool:
    for parent in a.parents:
        name = getattr(parent, "name", None)
        if name in ("b", "strong"):
            return True
        if name == "font" and str(parent.get("color") or "").lower() in ("red", "#ff0000"):
            return True
    return False


def parse_headlines(
    html: str | bytes | None,
    limit: int = MAX_ITEMS,
) -> list[dict[str, str | bool]]:
    """Parse the Drudge front page into headline dicts."""
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    headlines: list[dict[str, str | bool]] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = str(a["href"]).strip()
        text = a.get_text(" ", strip=True)
        if not _is_headline_link(href, text) or href in seen:
            continue
        seen.add(href)
        headlines.append(
            {
                "title": text,
                "link": href,
                "source": urlparse(href).netloc.replace("www.", ""),
                "top": _is_emphasized(a),
            }
        )
        if len(headlines) >= limit:
            break

    return headlines


def scrape() -> list[dict[str, str | bool]]:
    """Fetch Drudge headlines, write DRUDGEheadlines.txt, and append links to CSV."""
    try:
        resp = get(URL)
        headlines = parse_headlines(resp.content)
    except requests.RequestException as err:
        logger.error("Drudge request failed: %s", err)
        headlines = []
    except Exception as err:
        logger.error("Drudge parse failed: %s", err)
        headlines = []

    try:
        with Path("DRUDGEheadlines.txt").open("w", encoding="utf-8") as output_file:
            output_file.write(
                "--------------\n--------------\n"
                "Drudge Headlines\n"
                "--------------\n--------------\n\n"
            )
            if not headlines:
                output_file.write("(no headlines found - site layout may have changed)\n")
            for h in headlines:
                tag = "[TOP] " if h["top"] else ""
                output_file.write(tag + str(h["title"]) + "\n")
                if h["source"]:
                    output_file.write("(" + str(h["source"]) + ")\n")
                output_file.write(str(h["link"]) + "\n\n")
                append_row(str(h["title"]), str(h["link"]))
    except OSError as e:
        logger.error("Failed to write DRUDGEheadlines.txt: %s", e)
        return headlines

    logger.info("Wrote %d headlines to DRUDGEheadlines.txt", len(headlines))
    return headlines
