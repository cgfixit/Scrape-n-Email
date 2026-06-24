# test_mailer_csv.py — Unit/integration tests for csv_helper and mailer.
#
# All tests are offline: file I/O uses temp directories; SMTP calls are mocked.
#
# Run:  python -m unittest test_mailer_csv -v
#       python -m unittest discover -v   (picks up both test files)

import csv
import os
import smtplib
import tempfile
import unittest
from email.message import EmailMessage
from unittest.mock import MagicMock, patch

import csv_helper
import mailer


# ---------------------------------------------------------------------------
# csv_helper._csv_safe
# ---------------------------------------------------------------------------

class CsvSafeTests(unittest.TestCase):
    """_csv_safe must neutralise formula-injection prefixes and leave normal
    text untouched."""

    def test_equals_prefix_escaped(self):
        self.assertEqual(csv_helper._csv_safe("=SUM(A1:A10)"), "'=SUM(A1:A10)")

    def test_plus_prefix_escaped(self):
        self.assertEqual(csv_helper._csv_safe("+1234"), "'+1234")

    def test_minus_prefix_escaped(self):
        self.assertEqual(csv_helper._csv_safe("-SUM(A1)"), "'-SUM(A1)")

    def test_at_prefix_escaped(self):
        self.assertEqual(csv_helper._csv_safe("@formula"), "'@formula")

    def test_tab_prefix_escaped(self):
        self.assertEqual(csv_helper._csv_safe("\tleading"), "'\tleading")

    def test_cr_prefix_escaped(self):
        self.assertEqual(csv_helper._csv_safe("\rleading"), "'\rleading")

    def test_normal_text_unchanged(self):
        self.assertEqual(csv_helper._csv_safe("Hello World"), "Hello World")

    def test_url_unchanged(self):
        url = "https://example.com/path?q=1"
        self.assertEqual(csv_helper._csv_safe(url), url)

    def test_none_returns_empty_string(self):
        self.assertEqual(csv_helper._csv_safe(None), "")

    def test_empty_string_unchanged(self):
        self.assertEqual(csv_helper._csv_safe(""), "")

    def test_integer_converted_to_string(self):
        self.assertEqual(csv_helper._csv_safe(42), "42")

    def test_mid_string_special_chars_unchanged(self):
        # Only the *first* character triggers escaping.
        self.assertEqual(csv_helper._csv_safe("normal=stuff"), "normal=stuff")


# ---------------------------------------------------------------------------
# csv_helper.csvinit + csv_helper.writer (file I/O, temp directory)
# ---------------------------------------------------------------------------

class CsvFileTests(unittest.TestCase):
    """File-level tests that run in an isolated temporary directory."""

    def setUp(self):
        self._orig_dir = os.getcwd()
        self._tmpdir = tempfile.mkdtemp()
        os.chdir(self._tmpdir)

    def tearDown(self):
        os.chdir(self._orig_dir)

    # ------------------------------------------------------------------
    def _read_rows(self):
        with open("RCPlinks.csv", newline="", encoding="utf-8") as f:
            return list(csv.reader(f))

    # ------------------------------------------------------------------
    def test_csvinit_creates_file(self):
        csv_helper.csvinit()
        self.assertTrue(os.path.exists("RCPlinks.csv"))

    def test_csvinit_returns_true_on_success(self):
        self.assertTrue(csv_helper.csvinit())

    def test_csvinit_writes_header_row(self):
        csv_helper.csvinit()
        rows = self._read_rows()
        self.assertEqual(rows[0], ["HEADLINE", "URL"])

    def test_csvinit_overwrites_garbage_content(self):
        with open("RCPlinks.csv", "w") as f:
            f.write("garbage\n")
        csv_helper.csvinit()
        rows = self._read_rows()
        self.assertEqual(rows[0], ["HEADLINE", "URL"])

    def test_csvinit_returns_false_on_permission_error(self):
        # Simulate an unwritable file.
        with patch("builtins.open", side_effect=OSError("permission denied")):
            result = csv_helper.csvinit()
        self.assertFalse(result)

    def test_writer_appends_row(self):
        csv_helper.csvinit()
        csv_helper.writer("Test Headline", "https://example.com/article")
        rows = self._read_rows()
        data = [r for r in rows if r and r[0] not in ("HEADLINE", "")]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][0], "Test Headline")
        self.assertEqual(data[0][1], "https://example.com/article")

    def test_writer_returns_true_on_success(self):
        csv_helper.csvinit()
        self.assertTrue(csv_helper.writer("Title", "https://a.com/1"))

    def test_writer_appends_multiple_rows(self):
        csv_helper.csvinit()
        csv_helper.writer("Story One", "https://a.com/1")
        csv_helper.writer("Story Two", "https://b.com/2")
        rows = self._read_rows()
        data = [r for r in rows if r and r[0] not in ("HEADLINE", "")]
        self.assertEqual(len(data), 2)

    def test_writer_neutralizes_formula_injection(self):
        csv_helper.csvinit()
        csv_helper.writer("=MALICIOUS()", "https://safe.com/ok")
        rows = self._read_rows()
        data = [r for r in rows if r and r[0] not in ("HEADLINE", "")]
        self.assertEqual(data[0][0], "'=MALICIOUS()")

    def test_writer_returns_false_on_permission_error(self):
        csv_helper.csvinit()
        with patch("builtins.open", side_effect=OSError("permission denied")):
            result = csv_helper.writer("Title", "https://x.com/1")
        self.assertFalse(result)


# ---------------------------------------------------------------------------
# mailer._attach_file
# ---------------------------------------------------------------------------

class MailerAttachFileTests(unittest.TestCase):
    def test_missing_file_returns_false(self):
        msg = EmailMessage()
        self.assertFalse(mailer._attach_file(msg, "/nonexistent/path/file.txt"))

    def test_missing_file_does_not_add_attachment(self):
        msg = EmailMessage()
        mailer._attach_file(msg, "/nonexistent/path/file.txt")
        self.assertEqual(list(msg.iter_attachments()), [])

    def test_existing_file_returns_true(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"hello")
            path = f.name
        try:
            msg = EmailMessage()
            self.assertTrue(mailer._attach_file(msg, path))
        finally:
            os.unlink(path)

    def test_existing_file_adds_one_attachment(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"attachment body")
            path = f.name
        try:
            msg = EmailMessage()
            mailer._attach_file(msg, path)
            self.assertEqual(len(list(msg.iter_attachments())), 1)
        finally:
            os.unlink(path)

    def test_unreadable_file_returns_false(self):
        msg = EmailMessage()
        with patch("builtins.open", side_effect=OSError("permission denied")):
            with patch("os.path.isfile", return_value=True):
                self.assertFalse(mailer._attach_file(msg, "/fake/file.txt"))


# ---------------------------------------------------------------------------
# mailer.send_email
# ---------------------------------------------------------------------------

class MailerSendEmailTests(unittest.TestCase):
    def setUp(self):
        for key in ("EMAIL_USER", "EMAIL_PASS", "EMAIL_RECIPIENT"):
            os.environ.pop(key, None)

    def tearDown(self):
        for key in ("EMAIL_USER", "EMAIL_PASS", "EMAIL_RECIPIENT"):
            os.environ.pop(key, None)

    # ------------------------------------------------------------------
    def test_missing_both_credentials_returns_false(self):
        self.assertFalse(mailer.send_email("Subject", "Body", []))

    def test_missing_password_returns_false(self):
        os.environ["EMAIL_USER"] = "user@example.com"
        self.assertFalse(mailer.send_email("Subject", "Body", []))

    def test_missing_user_returns_false(self):
        os.environ["EMAIL_PASS"] = "apppassword"
        self.assertFalse(mailer.send_email("Subject", "Body", []))

    @patch("smtplib.SMTP")
    def test_successful_send_returns_true(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "user@example.com"
        os.environ["EMAIL_PASS"] = "apppassword"
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        self.assertTrue(mailer.send_email("Subject", "Body", []))

    @patch("smtplib.SMTP")
    def test_successful_send_calls_login_and_send(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "user@example.com"
        os.environ["EMAIL_PASS"] = "apppassword"
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        mailer.send_email("Subj", "Body", [])
        mock_server.login.assert_called_once_with("user@example.com", "apppassword")
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_default_recipient_is_sender(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "self@example.com"
        os.environ["EMAIL_PASS"] = "pass"
        sent_msgs = []
        mock_server = MagicMock()
        mock_server.send_message.side_effect = sent_msgs.append
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        mailer.send_email("S", "B", [])
        self.assertEqual(sent_msgs[0]["To"], "self@example.com")

    @patch("smtplib.SMTP")
    def test_explicit_recipient_used_when_set(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "sender@example.com"
        os.environ["EMAIL_PASS"] = "pass"
        os.environ["EMAIL_RECIPIENT"] = "boss@example.com"
        sent_msgs = []
        mock_server = MagicMock()
        mock_server.send_message.side_effect = sent_msgs.append
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        mailer.send_email("S", "B", [])
        self.assertEqual(sent_msgs[0]["To"], "boss@example.com")

    @patch("smtplib.SMTP")
    def test_auth_error_returns_false(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "user@example.com"
        os.environ["EMAIL_PASS"] = "wrongpass"
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        self.assertFalse(mailer.send_email("Subject", "Body", []))

    @patch("smtplib.SMTP")
    def test_smtp_exception_returns_false(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "user@example.com"
        os.environ["EMAIL_PASS"] = "pass"
        mock_smtp_cls.side_effect = smtplib.SMTPException("SMTP failure")
        self.assertFalse(mailer.send_email("Subject", "Body", []))

    @patch("smtplib.SMTP")
    def test_network_error_returns_false(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "user@example.com"
        os.environ["EMAIL_PASS"] = "pass"
        mock_smtp_cls.side_effect = OSError("Network unreachable")
        self.assertFalse(mailer.send_email("Subject", "Body", []))

    @patch("smtplib.SMTP")
    def test_connection_refused_returns_false(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "user@example.com"
        os.environ["EMAIL_PASS"] = "pass"
        mock_smtp_cls.side_effect = ConnectionRefusedError("Connection refused")
        self.assertFalse(mailer.send_email("Subject", "Body", []))

    @patch("smtplib.SMTP")
    def test_timeout_error_returns_false(self, mock_smtp_cls):
        os.environ["EMAIL_USER"] = "user@example.com"
        os.environ["EMAIL_PASS"] = "pass"
        mock_smtp_cls.side_effect = TimeoutError("Timed out")
        self.assertFalse(mailer.send_email("Subject", "Body", []))


# ---------------------------------------------------------------------------
# mailer.send_all
# ---------------------------------------------------------------------------

class MailerSendAllTests(unittest.TestCase):
    @patch("mailer.send_email")
    def test_send_all_calls_send_email_twice(self, mock_send):
        mock_send.return_value = True
        mailer.send_all()
        self.assertEqual(mock_send.call_count, 2)

    @patch("mailer.send_email")
    def test_send_all_subjects_contain_datestamp(self, mock_send):
        from datetime import date
        mock_send.return_value = True
        mailer.send_all()
        datestamp = date.today().strftime("%m-%d-%Y")
        subjects = [call[1].get("subject") or call[0][0] for call in mock_send.call_args_list]
        self.assertTrue(all(datestamp in s for s in subjects))

    @patch("mailer.send_email")
    def test_send_all_sends_news_and_jobs(self, mock_send):
        mock_send.return_value = True
        mailer.send_all()
        subjects = [call[1].get("subject") or call[0][0] for call in mock_send.call_args_list]
        self.assertTrue(any("News" in s for s in subjects))
        self.assertTrue(any("Jobs" in s for s in subjects))


# ---------------------------------------------------------------------------
# main.py orchestration
# ---------------------------------------------------------------------------

class MainOrchestratorTests(unittest.TestCase):
    @patch("clistScraper.scrape")
    @patch("rcpScraper.scrape")
    def test_main_calls_both_scrapers(self, mock_rcp, mock_clist):
        import main
        main.main()
        mock_rcp.assert_called_once()
        mock_clist.assert_called_once()

    @patch("clistScraper.scrape")
    @patch("rcpScraper.scrape", side_effect=RuntimeError("unexpected crash"))
    def test_main_continues_if_rcp_raises(self, _mock_rcp, mock_clist):
        # A hard crash in one scraper must not prevent the other from running.
        import main
        main.main()
        mock_clist.assert_called_once()

    @patch("clistScraper.scrape", side_effect=RuntimeError("unexpected crash"))
    @patch("rcpScraper.scrape")
    def test_main_continues_if_clist_raises(self, mock_rcp, _mock_clist):
        import main
        main.main()
        mock_rcp.assert_called_once()


if __name__ == "__main__":
    unittest.main()
