"""Tests for HTTP base.get() retry and failure paths."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from scrape_n_email.scrapers import base


def test_get_retries_on_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    session = MagicMock()
    session.get.side_effect = requests.ConnectionError("refused")
    monkeypatch.setattr(base, "get_session", lambda: session)
    monkeypatch.setattr(base.time, "sleep", lambda _: None)

    with pytest.raises(requests.ConnectionError, match="refused"):
        base.get("https://example.com")
    assert session.get.call_count == 3


def test_get_succeeds_on_second_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    good_resp = MagicMock()
    session = MagicMock()
    session.get.side_effect = [requests.Timeout("timeout"), good_resp]
    monkeypatch.setattr(base, "get_session", lambda: session)
    monkeypatch.setattr(base.time, "sleep", lambda _: None)

    result = base.get("https://example.com")
    assert result is good_resp
    assert session.get.call_count == 2


def test_get_raises_on_bad_status(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("404")
    session = MagicMock()
    session.get.return_value = response
    monkeypatch.setattr(base, "get_session", lambda: session)
    monkeypatch.setattr(base.time, "sleep", lambda _: None)

    with pytest.raises(requests.HTTPError, match="404"):
        base.get("https://example.com")


def test_get_passes_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    session = MagicMock()
    session.get.return_value = response
    monkeypatch.setattr(base, "get_session", lambda: session)

    base.get("https://example.com", timeout=5)
    session.get.assert_called_once_with("https://example.com", timeout=5)


def test_session_has_retry_adapter() -> None:
    base._session = None
    try:
        session = base.get_session()
        assert "https://" in session.adapters
        assert "http://" in session.adapters
        assert session.headers.get("User-Agent")
    finally:
        base._session = None
