# rcpScraper.py — RealClearPolitics homepage headlines / trending
#
# Writes RCPheadlines.txt and appends (title, link) rows to RCPlinks.csv via
# csv_helper.writer(). Called from main.py via scrape(); runnable standalone.
#
# The old `div.story` selector is gone. RCP is JS-heavy, but the server still
# renders article anchors in the static HTML, so we target the headline
# containers first and fall back to RCP article-URL patterns.

from bs4 import BeautifulSoup
import requests
import time
import os
import datetime
from urllib.parse import urljoin, urlparse
import csv_helper

URL = "https://www.realclearpolitics.com/"
MAX_ITEMS = 25

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# RCP article/content paths used to recognize real headlines in the fallback.
# Years are computed at import time so the filter stays valid across year boundaries.
_this_year = datetime.date.today().year
_CONTENT_HINTS = (
    "/articles/", "/video/", "/politics/",
    f"/{_this_year - 1}/",
    f"/{_this_year}/",
    f"/{_this_year + 1}/",
)
# Social/ad hosts (matched as exact host or true subdomain) and nav path
# segments (matched against the first path segment, extension stripped) — not
# loose substrings, so a look-alike like 'netflix.com' isn't matched by 'x.com'.
_SKIP_HOSTS = ("facebook.com", "twitter.com", "x.com", "instagram.com", "youtube.com")
_SKIP_PATH_SEGMENTS = {"about", "privacy", "faq", "contact", "advertise", "rss", "terms"}


def _get(url):
    # Fetch a URL with browser headers, a timeout, and simple backoff retries.
    sess = requests.Session()
    last_err = None
    for attempt in range(3):
        try:
            resp = sess.get(url, headers=_HEADERS, timeout=20)
            resp.raise_for_status()
            return resp
        except requests.RequestException as err:
            last_err = err
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise last_err


def _looks_like_headline(href, text):
    if not href or len(text) < 12:
        return False
    parsed = urlparse(href.lower())
    # Reject non-web schemes (mailto:, javascript:); relative hrefs have no scheme.
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return False
    host = parsed.netloc
    if any(host == h or host.endswith("." + h) for h in _SKIP_HOSTS):
        return False
    segments = [s for s in parsed.path.split("/") if s]
    if segments and segments[0].rsplit(".", 1)[0] in _SKIP_PATH_SEGMENTS:
        return False
    low = href.lower()
    # Keep RCP content paths or links that clearly point at an article page.
    return any(h in low for h in _CONTENT_HINTS) or low.endswith(".html")


def _collect(anchors, base, limit):
    # Filter anchors to headline dicts, de-duplicating by absolute URL.
    headlines = []
    seen = set()
    for a in anchors:
        href = (a.get("href") or "").strip()
        if not href:
            continue
        text = a.get_text(" ", strip=True)
        if not _looks_like_headline(href, text):
            continue
        link = urljoin(base, href)  # RCP uses relative hrefs; make absolute.
        if link in seen:
            continue
        seen.add(link)
        headlines.append({
            "title": text,
            "link": link,
            "source": urlparse(link).netloc.replace("www.", ""),
        })
        if len(headlines) >= limit:
            break
    return headlines


def parse_headlines(html, base=URL, limit=MAX_ITEMS):
    # Parse RCP homepage HTML into a list of headline dicts (title, link, source).

    # Pure function (no network/IO) for unit testing. Tries structured headline
    # containers first, then falls back to article-URL pattern matching so it
    # keeps working even if RCP renames its CSS classes.

    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")

    # 1) Preferred: known/likely headline containers. (`[class*='story']`
    #    subsumes `div.story`, so no separate `div.story` selector is needed.)
    preferred = []
    for selector in ("[class*='trending'] a", "[class*='headline'] a", "[class*='story'] a"):
        preferred.extend(soup.select(selector))

    headlines = _collect(preferred, base, limit)

    # 2) Fallback: if the containers yielded no *usable* headlines (e.g. they
    #    exist but their links don't match), scan every anchor on the page.
    if not headlines:
        headlines = _collect(soup.find_all("a", href=True), base, limit)

    return headlines


def scrape():
    # Fetch RCP headlines, write RCPheadlines.txt, append (title, link) to CSV.
    # CSV header is ensured once per run if file missing or empty (fixes legacy
    # "no header on first run" issue without duplicating headers).
    csv_file = 'RCPlinks.csv'
    if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
        csv_helper.csvinit()

    try:
        resp = _get(URL)
        headlines = parse_headlines(resp.content)
    except requests.RequestException as err:
        print(f"[rcp] request failed: {err}")
        headlines = []
    except Exception as err:  # parsing guard
        print(f"[rcp] parse failed: {err}")
        headlines = []

    try:
        with open('RCPheadlines.txt', 'w+', encoding="utf-8") as outputFile:
            outputFile.write('--------------\n--------------\nRCP Headlines\n--------------\n--------------\n\n')
            if not headlines:
                outputFile.write("(no headlines found — site layout may have changed)\n")
            for h in headlines:
                outputFile.write(h["title"] + "\n")
                if h["source"]:
                    outputFile.write("(" + h["source"] + ")\n")
                outputFile.write(h["link"] + "\n\n")
                csv_helper.writer(h["title"], h["link"])
    except OSError as e:
        print(f"[rcp] failed to write RCPheadlines.txt: {e}")
        return headlines

    print(f"[rcp] wrote {len(headlines)} headlines to RCPheadlines.txt")
    return headlines


if __name__ == "__main__":
    scrape()
