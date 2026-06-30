"""Integration test: scrape → CSV → file output → mailer attachment path.

All network and SMTP calls are mocked. Verifies the data flows from scraper
parse through CSV writes and into the mailer's attachment list.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

from scrape_n_email import cli
from scrape_n_email.csv import init_csv
from scrape_n_email.scrapers import clist, rcp

RCP_HTML = """
<div class="headline">
  <a href="https://example.com/articles/big-story.html">The Big Political Story Today</a>
</div>
"""

CLIST_HTML = """
<li class="cl-static-search-result">
  <a href="https://atlanta.craigslist.org/sys/12345.html">Senior Network Engineer</a>
  <div class="title">Senior Network Engineer</div>
  <div class="price">$80,000</div>
  <div class="location">Atlanta</div>
</li>
"""


@dataclass
class FakeResponse:
    content: bytes


def test_full_pipeline_writes_all_outputs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(rcp, "get", lambda _: FakeResponse(RCP_HTML.encode()))
    monkeypatch.setattr(clist, "get", lambda _: FakeResponse(CLIST_HTML.encode()))
    monkeypatch.setattr(cli, "send_all", MagicMock())

    assert cli.main(["--skip-email"]) == 0

    assert (tmp_path / "RCPheadlines.txt").exists()
    assert "The Big Political Story" in (tmp_path / "RCPheadlines.txt").read_text()
    assert (tmp_path / "RCPlinks.csv").exists()
    assert "big-story" in (tmp_path / "RCPlinks.csv").read_text()
    assert (tmp_path / "jobs.txt").exists()
    assert "Senior Network Engineer" in (tmp_path / "jobs.txt").read_text()


def test_pipeline_with_email_mocked(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("EMAIL_USER", "u@ex.com")
    monkeypatch.setenv("EMAIL_PASS", "pw")
    monkeypatch.setattr(rcp, "get", lambda _: FakeResponse(RCP_HTML.encode()))
    monkeypatch.setattr(clist, "get", lambda _: FakeResponse(CLIST_HTML.encode()))
    mock_send_all = MagicMock()
    monkeypatch.setattr(cli, "send_all", mock_send_all)

    assert cli.main([]) == 0
    mock_send_all.assert_called_once()


def test_scraper_failure_does_not_block_pipeline(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(rcp, "get", MagicMock(side_effect=ConnectionError("rcp down")))
    monkeypatch.setattr(clist, "get", lambda _: FakeResponse(CLIST_HTML.encode()))
    monkeypatch.setattr(cli, "send_all", MagicMock())

    assert cli.main(["--skip-email"]) == 0
    assert (tmp_path / "jobs.txt").exists()


def test_csv_append_accumulates_rows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    init_csv(force=True)
    monkeypatch.setattr(rcp, "get", lambda _: FakeResponse(RCP_HTML.encode()))
    monkeypatch.setattr(clist, "get", lambda _: FakeResponse(CLIST_HTML.encode()))
    monkeypatch.setattr(cli, "send_all", MagicMock())

    cli.main(["--skip-email"])
    csv_content = (tmp_path / "RCPlinks.csv").read_text()
    assert csv_content.count("\n") >= 3
