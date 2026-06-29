"""Tests for CLI orchestration."""

from __future__ import annotations

from unittest.mock import MagicMock

from scrape_n_email import cli


def test_main_skip_email_runs_scrapers(monkeypatch) -> None:
    monkeypatch.setattr(cli, "init_csv", MagicMock(return_value=True))
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock())
    monkeypatch.setattr(cli.clist, "scrape", MagicMock())
    monkeypatch.setattr(cli, "send_all", MagicMock())

    assert cli.main(["--skip-email"]) == 0
    cli.rcp.scrape.assert_called_once()
    cli.clist.scrape.assert_called_once()
    cli.send_all.assert_not_called()


def test_main_requires_email_config(monkeypatch) -> None:
    monkeypatch.delenv("EMAIL_USER", raising=False)
    monkeypatch.delenv("EMAIL_PASS", raising=False)

    assert cli.main([]) == 1


def test_main_sends_email(monkeypatch) -> None:
    monkeypatch.setenv("EMAIL_USER", "u@example.com")
    monkeypatch.setenv("EMAIL_PASS", "pass")
    monkeypatch.setattr(cli, "init_csv", MagicMock(return_value=True))
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock())
    monkeypatch.setattr(cli.clist, "scrape", MagicMock())
    monkeypatch.setattr(cli, "send_all", MagicMock())

    assert cli.main([]) == 0
    cli.send_all.assert_called_once()


def test_drudge_main_runs_drudge_and_rcp(monkeypatch) -> None:
    monkeypatch.setattr(cli, "init_csv", MagicMock(return_value=True))
    monkeypatch.setattr(cli.drudge, "scrape", MagicMock())
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock())

    assert cli.drudge_main([]) == 0
    cli.drudge.scrape.assert_called_once()
    cli.rcp.scrape.assert_called_once()
