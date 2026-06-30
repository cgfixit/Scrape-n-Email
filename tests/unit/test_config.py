"""Tests for environment configuration."""

from __future__ import annotations

import pytest

from scrape_n_email.config import Config


def test_from_env_loads_email(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_USER", "user@example.com")
    monkeypatch.setenv("EMAIL_PASS", "pass")
    monkeypatch.setenv("SMTP_PORT", "2525")

    config = Config.from_env()

    assert config.email_user == "user@example.com"
    assert config.email_pass == "pass"
    assert config.email_recipient == "user@example.com"
    assert config.smtp_port == 2525


def test_validate_requires_credentials() -> None:
    with pytest.raises(ValueError):
        Config().validate()
