# clistScraper.py — Atlanta sysadmin/networking ("sad") job listings
#
# Scrapes https://atlanta.craigslist.org/search/sad and writes the results to
# jobs.txt. Called from main.py via scrape(); also runnable standalone.
#
# Modern Craigslist serves its search results via JavaScript, but it still
# emits a no-JS fallback list of <li class="cl-static-search-result"> elements
# in the static HTML — that is what we parse here (no headless browser needed).

from bs4 import BeautifulSoup
import requests
import time

URL = "https://atlanta.craigslist.org/search/sad"
MAX_ITEMS = 25

# Realistic browser headers — the default python-requests UA gets 403'd.
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


def _clean(node):
    # Return stripped text for a bs4 node, or '' if the node is missing.
    return node.get_text(strip=True) if node else ""


def parse_jobs(html, limit=MAX_ITEMS):
    # Parse Craigslist search HTML into a list of job dicts.

    # Pure function (no network/IO) so it can be unit-tested against fixtures.
    # Returns dicts with: title, link, price, location, date.

    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    seen = set()

    # Primary: the no-JS static results block Craigslist still ships.
    results = soup.select("li.cl-static-search-result")

    # Fallback: the JS-rendered list, if the static block is ever dropped.
    if not results:
        results = soup.select("li.cl-search-result")

    for li in results:
        a = li.find("a", href=True)
        if not a:
            continue
        link = a["href"].strip()
        # Craigslist hrefs are already absolute — do NOT prepend a domain.
        if not link.startswith("http"):
            continue
        if link in seen:
            continue

        title = _clean(li.find("div", class_="title")) or (li.get("title") or "").strip() or _clean(a)
        if not title:
            continue

        price = _clean(li.find("div", class_="price")) or _clean(li.find("span", class_="priceinfo"))
        location = _clean(li.find("div", class_="location"))
        date_node = li.find("div", class_="meta") or li.find("time")
        date = _clean(date_node)

        seen.add(link)
        jobs.append({
            "title": title,
            "link": link,
            "price": price,
            "location": location,
            "date": date,
        })
        if len(jobs) >= limit:
            break

    return jobs


def scrape():
    # Fetch Atlanta sysadmin/networking jobs and write them to jobs.txt.
    try:
        resp = _get(URL)
        jobs = parse_jobs(resp.content)
    except requests.RequestException as err:
        print(f"[clist] request failed: {err}")
        jobs = []
    except Exception as err:  # parsing guard so main.py keeps running
        print(f"[clist] parse failed: {err}")
        jobs = []

    # Truncate ('w') so jobs.txt reflects only the current run.
    try:
        with open("jobs.txt", "w", encoding="utf-8") as out:
            out.write("---------------------\n")
            out.write("System/Network Admin Job Listings:\n")
            out.write("---------------------\n")
            if not jobs:
                out.write("(no listings found — site layout may have changed)\n")
            for job in jobs:
                meta = " · ".join(p for p in (job["price"], job["location"], job["date"]) if p)
                out.write(job["title"] + "\n")
                if meta:
                    out.write(meta + "\n")
                out.write(job["link"] + "\n\n")
    except OSError as e:
        print(f"[clist] failed to write jobs.txt: {e}")
        return jobs

    print(f"[clist] wrote {len(jobs)} listings to jobs.txt")
    return jobs


if __name__ == "__main__":
    scrape()
