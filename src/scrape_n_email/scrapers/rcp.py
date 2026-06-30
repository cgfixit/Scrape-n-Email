"""RealClearPolitics homepage scraper."""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from scrape_n_email.csv import append_rows, init_csv
from scrape_n_email.scrapers.base import get

logger = logging.getLogger("scrape_n_email.scrapers.rcp")

URL = "https://www.realclearpolitics.com/"
MAX_ITEMS = 25

_CONTENT_HINTS = ("/articles/", "/video/", "/politics/", "/2024/", "/2025/", "/2026/")
_SKIP_HOSTS = ("facebook.com", "twitter.com", "x.com", "instagram.com", "youtube.com")
_SKIP_PATH_SEGMENTS = {"about", "privacy", "faq", "contact", "advertise", "rss", "terms"}


def _looks_like_headline(href: str, text: str) -> bool:
    if not href or len(text) < 12:
        return False
    parsed = urlparse(href.lower())
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return False
    host = parsed.netloc
    if any(host == h or host.endswith("." + h) for h in _SKIP_HOSTS):
        return False
    segments = [s for s in parsed.path.split("/") if s]
    if segments and segments[0].rsplit(".", 1)[0] in _SKIP_PATH_SEGMENTS:
        return False
    low = href.lower()
    return any(h in low for h in _CONTENT_HINTS) or low.endswith(".html")


def _collect(anchors: list[Tag], base: str, limit: int) -> list[dict[str, str]]:
    headlines: list[dict[str, str]] = []
    seen: set[str] = set()
    for a in anchors:
        href = str(a.get("href") or "").strip()
        if not href:
            continue
        text = a.get_text(" ", strip=True)
        if not _looks_like_headline(href, text):
            continue
        link = urljoin(base, href)
        if link in seen:
            continue
        seen.add(link)
        headlines.append(
            {
                "title": text,
                "link": link,
                "source": urlparse(link).netloc.replace("www.", ""),
            }
        )
        if len(headlines) >= limit:
            break
    return headlines


def parse_headlines(
    html: str | bytes | None,
    base: str = URL,
    limit: int = MAX_ITEMS,
) -> list[dict[str, str]]:
    """Parse RCP homepage HTML into headline dicts."""
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")

    preferred: list[Tag] = []
    for selector in ("[class*='trending'] a", "[class*='headline'] a", "[class*='story'] a"):
        preferred.extend(soup.select(selector))

    headlines = _collect(preferred, base, limit)
    if not headlines:
        headlines = _collect(soup.find_all("a", href=True), base, limit)
    return headlines


def scrape() -> list[dict[str, str]]:
    """Fetch RCP headlines, write RCPheadlines.txt, and append links to CSV."""
    if not Path("RCPlinks.csv").exists() or Path("RCPlinks.csv").stat().st_size == 0:
        init_csv()

    try:
        resp = get(URL)
        headlines = parse_headlines(resp.content)
    except requests.RequestException as err:
        logger.error("RCP request failed: %s", err)
        headlines = []
    except Exception as err:
        logger.error("RCP parse failed: %s", err)
        headlines = []

    try:
        with Path("RCPheadlines.txt").open("w", encoding="utf-8") as output_file:
            output_file.write(
                "--------------\n--------------\nRCP Headlines\n--------------\n--------------\n\n"
            )
            if not headlines:
                output_file.write("(no headlines found - site layout may have changed)\n")
            for h in headlines:
                output_file.write(h["title"] + "\n")
                if h["source"]:
                    output_file.write("(" + h["source"] + ")\n")
                output_file.write(h["link"] + "\n\n")
    except OSError as e:
        logger.error("Failed to write RCPheadlines.txt: %s", e)
        return headlines

    if headlines:
        append_rows((h["title"], h["link"]) for h in headlines)

    logger.info("Wrote %d headlines to RCPheadlines.txt", len(headlines))
    return headlines


if __name__ == "__main__":
    scrape()
