# drudgeScraper.py — Drudge Report headline scraper + CSV writer helper (legacy module name)
#
# The project originally started as a Drudge Report scraper, then pivoted to RCP.
# This module still contains a fully functional Drudge parser (for standalone use
# or future expansion) and now delegates CSV writing to csv_helper.py to avoid
# circular imports with rcpScraper.py.
#
# CSV functions (csvinit, writer, _csv_safe) live in csv_helper.py
#
# Called from main.py? No — only rcpScraper + clistScraper are orchestrated.
# This module's scrape() can be called manually or from its own __main__ block.

from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urlparse
import csv_helper   # CSV logic centralized here to break circular dependency

URL = "https://www.drudgereport.com/"
MAX_ITEMS = 60

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

# Substrings that mark a link as navigation/social/ad/self-reference rather
# than a news headline. Drudge has no stable classes, so we filter by href.
_SKIP_HOSTS = (
    "drudgereport.com", "drudgereportarchives.com", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "youtube.com", "t.me", "truthsocial.com",
    "googlesyndication.com", "doubleclick.net", "google.com",
)
# Nav/utility path segments that are never news headlines. Matched as whole
# path segments (not loose substrings) so a real story such as
# /about-face-on-tariffs is not dropped. Social/ad hosts are handled by
# _SKIP_HOSTS above. mailto:/javascript: are rejected by the http check.
_SKIP_PATH_SEGMENTS = {
    "privacy", "about", "contact", "rss", "advertise", "subscribe", "terms",
}


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


def _is_headline_link(href, text):
    # Heuristic: keep external article links with real headline text.
    if not href or not href.startswith("http"):
        return False
    parsed = urlparse(href.lower())
    host = parsed.netloc
    # Drop social/ad/self hosts — exact host or a true subdomain only, so a
    # look-alike like 'netflix.com' is not matched by 'x.com'.
    if any(host == h or host.endswith("." + h) for h in _SKIP_HOSTS):
        return False
    # Drop nav pages by whole-path-segment match (not loose substring).
    segments = [s for s in parsed.path.split("/") if s]
    if any(seg in _SKIP_PATH_SEGMENTS for seg in segments):
        return False
    # Headlines are sentence-like; skip stray one-word / image links.
    return len(text) >= 12


def _is_emphasized(a):
    # True if the anchor sits inside bold/red markup → likely a top/flash story.
    for parent in a.parents:
        name = getattr(parent, "name", None)
        if name in ("b", "strong"):
            return True
        if name == "font" and (parent.get("color") or "").lower() in ("red", "#ff0000"):
            return True
    return False


def parse_headlines(html, limit=MAX_ITEMS):
    # Parse the Drudge front page into a list of headline dicts.

    # Pure function (no network/IO) for unit testing. Returns dicts with:
    # title, link, source, top (bool). Order follows document order, which puts
    # the splash headline first, then the left/center/right columns.

    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    headlines = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(" ", strip=True)
        if not _is_headline_link(href, text):
            continue
        if href in seen:
            continue
        seen.add(href)
        headlines.append({
            "title": text,
            "link": href,
            "source": urlparse(href).netloc.replace("www.", ""),
            "top": _is_emphasized(a),
        })
        if len(headlines) >= limit:
            break

    return headlines


def scrape():
    # Fetch Drudge headlines, write DRUDGEheadlines.txt, and append to the CSV
    # via csv_helper (centralized, injection-safe).
    try:
        resp = _get(URL)
        headlines = parse_headlines(resp.content)
    except requests.RequestException as err:
        print(f"[drudge] request failed: {err}")
        headlines = []
    except Exception as err:  # parsing guard
        print(f"[drudge] parse failed: {err}")
        headlines = []

    try:
        with open('DRUDGEheadlines.txt', 'w+', encoding="utf-8") as outputFile:
            outputFile.write('--------------\n--------------\nDrudge Headlines\n--------------\n--------------\n\n')
            if not headlines:
                outputFile.write("(no headlines found — site layout may have changed)\n")
            for h in headlines:
                tag = "[TOP] " if h["top"] else ""
                outputFile.write(tag + h["title"] + "\n")
                if h["source"]:
                    outputFile.write("(" + h["source"] + ")\n")
                outputFile.write(h["link"] + "\n\n")
    except OSError as e:
        print(f"[drudge] failed to write DRUDGEheadlines.txt: {e}")
        return headlines

    # Write all CSV rows in one file open, independent of the txt write above.
    csv_helper.write_rows([(h["title"], h["link"]) for h in headlines])

    print(f"[drudge] wrote {len(headlines)} headlines to DRUDGEheadlines.txt")
    return headlines


# Below only runs if program is ran independently; in main.py we only call
# rcpScraper.scrape() + clistScraper.scrape(). The CSV work is now in csv_helper.
if __name__ == "__main__":
    import rcpScraper   # lazy import to avoid any potential circularity at module load

    csv_helper.csvinit()
    csv_helper.writer("~DRUDGE", "  ~~~")
    scrape()
    csv_helper.writer("~REALCLEARPOLITICS", "  ~~~")
    rcpScraper.scrape()
    print("[drudge __main__] Standalone run complete.")
