"""Edge-case tests for mailer: error classification, network errors, retry behavior."""

from __future__ import annotations

import os
import smtplib
from pathlib import Path
from unittest.mock import MagicMock, patch

from scrape_n_email import mailer


def _clear_env() -> None:
    for key in ("EMAIL_USER", "EMAIL_PASS", "EMAIL_RECIPIENT"):
        os.environ.pop(key, None)


class TestTransientErrorClassification:
    def test_auth_error_is_not_transient(self) -> None:
        exc = smtplib.SMTPAuthenticationError(535, b"failed")
        assert mailer._is_transient_smtp_error(exc) is False

    def test_permanent_code_is_not_transient(self) -> None:
        exc = smtplib.SMTPResponseException(535, b"perm")
        assert mailer._is_transient_smtp_error(exc) is False

    def test_code_530_is_not_transient(self) -> None:
        exc = smtplib.SMTPResponseException(530, b"access denied")
        assert mailer._is_transient_smtp_error(exc) is False

    def test_transient_code_is_transient(self) -> None:
        exc = smtplib.SMTPResponseException(421, b"try again")
        assert mailer._is_transient_smtp_error(exc) is True

    def test_generic_smtp_exception_is_transient(self) -> None:
        exc = smtplib.SMTPException("generic")
        assert mailer._is_transient_smtp_error(exc) is True


class TestAttachFileErrors:
    def test_attach_read_oserror(self, tmp_path: Path) -> None:
        from email.message import EmailMessage

        path = tmp_path / "file.txt"
        path.write_text("data", encoding="utf-8")
        msg = EmailMessage()
        with patch.object(Path, "read_bytes", side_effect=OSError("perm denied")):
            assert mailer._attach_file(msg, path) is False

    def test_attach_unknown_mime_type(self, tmp_path: Path) -> None:
        from email.message import EmailMessage

        path = tmp_path / "file.xyz123"
        path.write_bytes(b"\x00\x01\x02")
        msg = EmailMessage()
        assert mailer._attach_file(msg, path) is True
        attachments = list(msg.iter_attachments())
        assert len(attachments) == 1


class TestNetworkErrors:
    @patch("time.sleep", return_value=None)
    @patch("smtplib.SMTP")
    def test_connection_refused_retries(self, mock_smtp_cls: MagicMock, _sleep: MagicMock) -> None:
        _clear_env()
        os.environ["EMAIL_USER"] = "u@ex.com"
        os.environ["EMAIL_PASS"] = "pw"
        mock_smtp_cls.side_effect = ConnectionRefusedError("refused")

        assert mailer.send_email("Subj", "Body", []) is False
        assert mock_smtp_cls.call_count == mailer._MAX_RETRIES
        _clear_env()

    @patch("time.sleep", return_value=None)
    @patch("smtplib.SMTP")
    def test_timeout_error_retries(self, mock_smtp_cls: MagicMock, _sleep: MagicMock) -> None:
        _clear_env()
        os.environ["EMAIL_USER"] = "u@ex.com"
        os.environ["EMAIL_PASS"] = "pw"
        mock_smtp_cls.side_effect = TimeoutError("timed out")

        assert mailer.send_email("Subj", "Body", []) is False
        assert mock_smtp_cls.call_count == mailer._MAX_RETRIES
        _clear_env()


class TestPermanentSmtpError:
    @patch("smtplib.SMTP")
    def test_permanent_smtp_code_not_retried(self, mock_smtp_cls: MagicMock) -> None:
        _clear_env()
        os.environ["EMAIL_USER"] = "u@ex.com"
        os.environ["EMAIL_PASS"] = "pw"
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPResponseException(535, b"perm error")
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        assert mailer.send_email("Subj", "Body", []) is False
        assert mock_smtp_cls.call_count == 1
        _clear_env()


class TestRecipientFallback:
    @patch("smtplib.SMTP")
    def test_recipient_defaults_to_sender(self, mock_smtp_cls: MagicMock) -> None:
        _clear_env()
        os.environ["EMAIL_USER"] = "sender@ex.com"
        os.environ["EMAIL_PASS"] = "pw"
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        mailer.send_email("Subj", "Body", [])
        sent_msg = mock_server.send_message.call_args[0][0]
        assert sent_msg["To"] == "sender@ex.com"
        _clear_env()


class TestSendAll:
    @patch("scrape_n_email.mailer.send_email", return_value=False)
    def test_send_all_logs_failure(self, mock_send: MagicMock) -> None:
        mailer.send_all()
        assert mock_send.call_count == 2

    @patch("scrape_n_email.mailer.send_email", return_value=True)
    def test_send_all_with_script_dir(self, mock_send: MagicMock, tmp_path: Path) -> None:
        mailer.send_all(script_dir=tmp_path)
        call_args = mock_send.call_args_list
        for call in call_args:
            attachments = call.kwargs.get("attachments", call.args[2] if len(call.args) > 2 else [])
            for att in attachments:
                assert str(att).startswith(str(tmp_path))
