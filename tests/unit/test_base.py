"""Tests for HTTP base helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from scrape_n_email.scrapers import base


def test_get_returns_response(monkeypatch) -> None:
    response = MagicMock()
    session = MagicMock()
    session.get.return_value = response
    monkeypatch.setattr(base, "get_session", lambda: session)

    assert base.get("https://example.com") is response
    response.raise_for_status.assert_called_once()
