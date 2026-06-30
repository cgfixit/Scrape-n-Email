"""Tests for scraper error handling: network failures, file write errors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from scrape_n_email.scrapers import clist, drudge, rcp


@dataclass
class FakeResponse:
    content: bytes


class TestRcpScrapeErrors:
    def test_request_exception_returns_empty(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(rcp, "get", MagicMock(side_effect=requests.ConnectionError("down")))
        result = rcp.scrape()
        assert result == []

    def test_parse_exception_returns_empty(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(rcp, "get", MagicMock(side_effect=TypeError("bad parse")))
        result = rcp.scrape()
        assert result == []

    def test_file_write_oserror(self, tmp_path: Path, monkeypatch) -> None:
        html = (
            '<div class="headline">'
            '<a href="https://example.com/articles/story.html">A Real Headline Here</a>'
            "</div>"
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(rcp, "get", lambda _: FakeResponse(html.encode()))
        with patch.object(Path, "open", side_effect=OSError("disk full")):
            result = rcp.scrape()
        assert isinstance(result, list)

    def test_empty_headlines_writes_fallback_message(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(rcp, "get", lambda _: FakeResponse(b"<html></html>"))
        rcp.scrape()
        content = (tmp_path / "RCPheadlines.txt").read_text()
        assert "no headlines found" in content


class TestClistScrapeErrors:
    def test_request_exception_returns_empty(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(clist, "get", MagicMock(side_effect=requests.Timeout("timeout")))
        result = clist.scrape()
        assert result == []

    def test_general_exception_returns_empty(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(clist, "get", MagicMock(side_effect=ValueError("unexpected")))
        result = clist.scrape()
        assert result == []

    def test_empty_jobs_writes_fallback(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(clist, "get", lambda _: FakeResponse(b"<html></html>"))
        clist.scrape()
        content = (tmp_path / "jobs.txt").read_text()
        assert "no listings found" in content


class TestDrudgeScrapeErrors:
    def test_request_exception_returns_empty(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(drudge, "get", MagicMock(side_effect=requests.ConnectionError("down")))
        result = drudge.scrape()
        assert result == []

    def test_general_exception_returns_empty(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(drudge, "get", MagicMock(side_effect=RuntimeError("weird")))
        result = drudge.scrape()
        assert result == []

    def test_empty_headlines_writes_fallback(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(drudge, "get", lambda _: FakeResponse(b"<html></html>"))
        drudge.scrape()
        content = (tmp_path / "DRUDGEheadlines.txt").read_text()
        assert "no headlines found" in content
