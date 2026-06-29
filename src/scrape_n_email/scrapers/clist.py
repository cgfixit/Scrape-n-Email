"""Atlanta Craigslist sysadmin/networking job scraper."""

from __future__ import annotations

import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement

from scrape_n_email.scrapers.base import get

logger = logging.getLogger("scrape_n_email.scrapers.clist")

URL = "https://atlanta.craigslist.org/search/sad"
MAX_ITEMS = 25


def _clean(node: PageElement | None) -> str:
    return node.get_text(strip=True) if node else ""


def parse_jobs(html: str | bytes | None, limit: int = MAX_ITEMS) -> list[dict[str, str]]:
    """Parse Craigslist search HTML into job dicts."""
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict[str, str]] = []
    seen: set[str] = set()

    results = soup.select("li.cl-static-search-result") or soup.select("li.cl-search-result")

    for li in results:
        a = li.find("a", href=True)
        if not a:
            continue
        link = str(a["href"]).strip()
        if not link.startswith("http") or link in seen:
            continue

        title = (
            _clean(li.find("div", class_="title"))
            or str(li.get("title") or "").strip()
            or _clean(a)
        )
        if not title:
            continue

        price = _clean(li.find("div", class_="price")) or _clean(
            li.find("span", class_="priceinfo")
        )
        location = _clean(li.find("div", class_="location"))
        date_node = li.find("div", class_="meta") or li.find("time")
        date = _clean(date_node)

        seen.add(link)
        jobs.append(
            {"title": title, "link": link, "price": price, "location": location, "date": date}
        )
        if len(jobs) >= limit:
            break

    return jobs


def scrape() -> list[dict[str, str]]:
    """Fetch Atlanta jobs and write them to jobs.txt."""
    try:
        resp = get(URL)
        jobs = parse_jobs(resp.content)
    except requests.RequestException as err:
        logger.error("Craigslist request failed: %s", err)
        jobs = []
    except Exception as err:
        logger.error("Craigslist parse failed: %s", err)
        jobs = []

    try:
        with Path("jobs.txt").open("w", encoding="utf-8") as out:
            out.write("---------------------\n")
            out.write("System/Network Admin Job Listings:\n")
            out.write("---------------------\n")
            if not jobs:
                out.write("(no listings found - site layout may have changed)\n")
            for job in jobs:
                meta = " - ".join(p for p in (job["price"], job["location"], job["date"]) if p)
                out.write(job["title"] + "\n")
                if meta:
                    out.write(meta + "\n")
                out.write(job["link"] + "\n\n")
    except OSError as e:
        logger.error("Failed to write jobs.txt: %s", e)
        return jobs

    logger.info("Wrote %d listings to jobs.txt", len(jobs))
    return jobs


if __name__ == "__main__":
    scrape()
