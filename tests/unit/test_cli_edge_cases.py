"""Edge-case tests for CLI: exception handling, scraper failures, drudge_main errors."""

from __future__ import annotations

from unittest.mock import MagicMock

from scrape_n_email import cli


def test_rcp_scraper_exception_is_caught(monkeypatch) -> None:
    monkeypatch.setattr(cli, "init_csv", MagicMock(return_value=True))
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock(side_effect=RuntimeError("rcp fail")))
    monkeypatch.setattr(cli.clist, "scrape", MagicMock())
    monkeypatch.setattr(cli, "send_all", MagicMock())

    assert cli.main(["--skip-email"]) == 0
    cli.clist.scrape.assert_called_once()


def test_clist_scraper_exception_is_caught(monkeypatch) -> None:
    monkeypatch.setattr(cli, "init_csv", MagicMock(return_value=True))
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock())
    monkeypatch.setattr(cli.clist, "scrape", MagicMock(side_effect=RuntimeError("clist fail")))
    monkeypatch.setattr(cli, "send_all", MagicMock())

    assert cli.main(["--skip-email"]) == 0


def test_send_all_exception_returns_error(monkeypatch) -> None:
    monkeypatch.setenv("EMAIL_USER", "u@ex.com")
    monkeypatch.setenv("EMAIL_PASS", "pw")
    monkeypatch.setattr(cli, "init_csv", MagicMock(return_value=True))
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock())
    monkeypatch.setattr(cli.clist, "scrape", MagicMock())
    monkeypatch.setattr(cli, "send_all", MagicMock(side_effect=RuntimeError("mail crash")))

    assert cli.main([]) == 1


def test_both_scrapers_fail_still_returns_zero(monkeypatch) -> None:
    monkeypatch.setattr(cli, "init_csv", MagicMock(return_value=True))
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock(side_effect=Exception("boom")))
    monkeypatch.setattr(cli.clist, "scrape", MagicMock(side_effect=Exception("boom")))
    monkeypatch.setattr(cli, "send_all", MagicMock())

    assert cli.main(["--skip-email"]) == 0


def test_drudge_main_calls_init_csv(monkeypatch) -> None:
    mock_init = MagicMock(return_value=True)
    monkeypatch.setattr(cli, "init_csv", mock_init)
    monkeypatch.setattr(cli.drudge, "scrape", MagicMock())
    monkeypatch.setattr(cli.rcp, "scrape", MagicMock())

    cli.drudge_main([])
    mock_init.assert_called_once_with(force=True)


def test_setup_logging_idempotent() -> None:
    cli.setup_logging()
    cli.setup_logging()
