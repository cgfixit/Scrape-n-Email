"""Shared HTTP session with retry logic and browser headers."""

from __future__ import annotations

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("scrape_n_email.scrapers")

_RETRY = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)

_DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_session: requests.Session | None = None


def get_session() -> requests.Session:
    """Return a shared requests Session with retry adapter and browser headers."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(_DEFAULT_HEADERS)
        adapter = HTTPAdapter(max_retries=_RETRY, pool_connections=10, pool_maxsize=10)
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
        logger.debug("Created new HTTP session with retry adapter")
    return _session


def get(url: str, timeout: int = 20) -> requests.Response:
    """Fetch a URL with the shared session, timeout, and exponential backoff retries."""
    last_err: requests.RequestException | None = None
    for attempt in range(3):
        try:
            resp = get_session().get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as err:
            last_err = err
            if attempt < 2:
                sleep_s = 2**attempt
                logger.warning(
                    "GET %s failed (attempt %d/3): %s; retrying in %ds",
                    url,
                    attempt + 1,
                    err,
                    sleep_s,
                )
                time.sleep(sleep_s)
    if last_err is not None:
        raise last_err
    raise requests.RequestException(f"GET {url} failed")
