"""Tests for SMTP mailer."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import MagicMock, patch

from scrape_n_email import mailer


def _clear_env() -> None:
    for key in ("EMAIL_USER", "EMAIL_PASS", "EMAIL_RECIPIENT"):
        os.environ.pop(key, None)


def test_attach_file_missing() -> None:
    msg = EmailMessage()
    assert mailer._attach_file(msg, Path("/nonexistent/path/file.txt")) is False
    assert list(msg.iter_attachments()) == []


def test_attach_file_existing(tmp_path: Path) -> None:
    path = tmp_path / "a.txt"
    path.write_text("hello", encoding="utf-8")
    msg = EmailMessage()
    assert mailer._attach_file(msg, path) is True
    assert len(list(msg.iter_attachments())) == 1


def test_missing_credentials_return_false() -> None:
    _clear_env()
    assert mailer.send_email("Subject", "Body", []) is False


@patch("smtplib.SMTP")
def test_successful_send(mock_smtp_cls: MagicMock) -> None:
    _clear_env()
    os.environ["EMAIL_USER"] = "user@example.com"
    os.environ["EMAIL_PASS"] = "apppassword"
    mock_server = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    assert mailer.send_email("Subject", "Body", []) is True
    mock_server.login.assert_called_once_with("user@example.com", "apppassword")
    mock_server.send_message.assert_called_once()
    _clear_env()


@patch("smtplib.SMTP")
def test_auth_error_not_retried(mock_smtp_cls: MagicMock) -> None:
    _clear_env()
    os.environ["EMAIL_USER"] = "user@example.com"
    os.environ["EMAIL_PASS"] = "wrong"
    mock_server = MagicMock()
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    assert mailer.send_email("Subject", "Body", []) is False
    assert mock_smtp_cls.call_count == 1
    _clear_env()


@patch("time.sleep", return_value=None)
@patch("smtplib.SMTP")
def test_transient_smtp_error_retries(mock_smtp_cls: MagicMock, _sleep: MagicMock) -> None:
    _clear_env()
    os.environ["EMAIL_USER"] = "user@example.com"
    os.environ["EMAIL_PASS"] = "pass"
    mock_smtp_cls.side_effect = smtplib.SMTPException("temporary")

    assert mailer.send_email("Subject", "Body", []) is False
    assert mock_smtp_cls.call_count == mailer._MAX_RETRIES
    _clear_env()


@patch("scrape_n_email.mailer.send_email", return_value=True)
def test_send_all_calls_send_email_twice(mock_send: MagicMock) -> None:
    mailer.send_all()
    assert mock_send.call_count == 2
