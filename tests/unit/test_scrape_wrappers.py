"""Tests for scraper IO wrappers with network mocked out."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scrape_n_email.scrapers import clist, drudge, rcp
from tests.unit.test_scrapers import CRAIGSLIST_HTML, DRUDGE_HTML, RCP_HTML


@dataclass
class FakeResponse:
    content: bytes


def test_rcp_scrape_writes_outputs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(rcp, "get", lambda _url: FakeResponse(RCP_HTML.encode()))

    headlines = rcp.scrape()

    assert len(headlines) == 3
    assert (tmp_path / "RCPheadlines.txt").exists()
    assert "The Big Political Story Today" in (tmp_path / "RCPheadlines.txt").read_text()
    assert "HEADLINE,URL" in (tmp_path / "RCPlinks.csv").read_text()


def test_clist_scrape_writes_jobs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(clist, "get", lambda _url: FakeResponse(CRAIGSLIST_HTML.encode()))

    jobs = clist.scrape()

    assert len(jobs) == 2
    assert "Senior Network Engineer" in (tmp_path / "jobs.txt").read_text()


def test_drudge_scrape_writes_outputs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(drudge, "get", lambda _url: FakeResponse(DRUDGE_HTML.encode()))

    headlines = drudge.scrape()

    assert len(headlines) == 6
    assert "SPLASH HEADLINE OF THE DAY" in (tmp_path / "DRUDGEheadlines.txt").read_text()
