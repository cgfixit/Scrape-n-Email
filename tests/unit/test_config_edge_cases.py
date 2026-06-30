"""Edge-case tests for Config: type coercion, fallback logic, boundary values."""

from __future__ import annotations

import pytest

from scrape_n_email.config import Config


def test_recipient_fallback_to_email_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_USER", "me@example.com")
    monkeypatch.setenv("EMAIL_PASS", "pw")
    monkeypatch.delenv("EMAIL_RECIPIENT", raising=False)

    cfg = Config.from_env()
    assert cfg.email_recipient == "me@example.com"


def test_explicit_recipient_overrides_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_USER", "sender@example.com")
    monkeypatch.setenv("EMAIL_PASS", "pw")
    monkeypatch.setenv("EMAIL_RECIPIENT", "other@example.com")

    cfg = Config.from_env()
    assert cfg.email_recipient == "other@example.com"


def test_non_numeric_smtp_port_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_PORT", "abc")
    with pytest.raises(ValueError):
        Config.from_env()


def test_non_numeric_max_items_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_RCP_ITEMS", "not_a_number")
    with pytest.raises(ValueError):
        Config.from_env()


def test_custom_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RCP_URL", "https://custom.rcp.com/")
    monkeypatch.setenv("CLIST_URL", "https://custom.clist.com/")
    monkeypatch.setenv("DRUDGE_URL", "https://custom.drudge.com/")

    cfg = Config.from_env()
    assert cfg.rcp_url == "https://custom.rcp.com/"
    assert cfg.clist_url == "https://custom.clist.com/"
    assert cfg.drudge_url == "https://custom.drudge.com/"


def test_custom_max_items(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_RCP_ITEMS", "10")
    monkeypatch.setenv("MAX_CLIST_ITEMS", "5")
    monkeypatch.setenv("MAX_DRUDGE_ITEMS", "100")

    cfg = Config.from_env()
    assert cfg.max_rcp_items == 10
    assert cfg.max_clist_items == 5
    assert cfg.max_drudge_items == 100


def test_empty_email_user_fails_validate() -> None:
    cfg = Config(email_user="", email_pass="pw")
    with pytest.raises(ValueError):
        cfg.validate()


def test_empty_email_pass_fails_validate() -> None:
    cfg = Config(email_user="user@example.com", email_pass="")
    with pytest.raises(ValueError):
        cfg.validate()


def test_valid_config_passes_validate() -> None:
    cfg = Config(email_user="u@ex.com", email_pass="pass")
    cfg.validate()


def test_default_values() -> None:
    cfg = Config()
    assert cfg.smtp_host == "smtp.gmail.com"
    assert cfg.smtp_port == 587
    assert cfg.max_rcp_items == 25
    assert cfg.max_clist_items == 25
    assert cfg.max_drudge_items == 60
