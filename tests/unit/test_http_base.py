"""Tests for shared HTTP session."""

from __future__ import annotations

from scrape_n_email.scrapers.base import get_session


def test_get_session_reuses_single_session() -> None:
    assert get_session() is get_session()
