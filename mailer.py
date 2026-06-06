# mailer.py — Pure Python replacement for sendEmail.exe + email.bat
#
# Requires: Python 3.6+, no external dependencies
#
# Environment variables (set before running):
#   EMAIL_USER      — Gmail address to send from
#   EMAIL_PASS      — Gmail App Password (NOT your regular password)
#   EMAIL_RECIPIENT — (optional) destination address; defaults to EMAIL_USER
#
# Gmail App Password setup:
#   Google Account → Security → 2-Step Verification → App Passwords
#   Generate a 16-character token and use that as EMAIL_PASS

import smtplib
import ssl
import os
import mimetypes
from datetime import date
from email.message import EmailMessage


def _attach_file(msg, filepath):
    # Attach a file to the email message if it exists.

    # Uses mimetypes to set the correct MIME type so email clients
    # render .txt and .csv attachments properly instead of treating
    # everything as a generic binary blob.
    
    if not os.path.isfile(filepath):
        print(f"  Warning: attachment not found, skipping: {filepath}")
        return False

    mime_type, _ = mimetypes.guess_type(filepath)
    maintype, subtype = (mime_type or "application/octet-stream").split("/")

    with open(filepath, "rb") as f:
        data = f.read()

    msg.add_attachment(
        data,
        maintype=maintype,
        subtype=subtype,
        filename=os.path.basename(filepath),
    )
    return True


def send_email(subject, body, attachments):
    # Send a single email with the given subject, body, and file attachments.

    # Returns True on success, False on failure.
    
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    recipient = os.environ.get("EMAIL_RECIPIENT", sender)

    if not sender or not password:
        print("Error: EMAIL_USER and EMAIL_PASS environment variables must be set.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    for filepath in attachments:
        _attach_file(msg, filepath)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.send_message(msg)
        print(f"  Sent: {subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"  Error: Authentication failed for '{subject}'.")
        print("  Check EMAIL_USER/EMAIL_PASS. Gmail requires an App Password.")
        return False
    except smtplib.SMTPException as e:
        print(f"  SMTP error sending '{subject}': {e}")
        return False
    except OSError as e:
        print(f"  Network error sending '{subject}': {e}")
        return False


def send_all():
    # Send the daily news and jobs emails.

    # This function fully replaces email.bat and sendEmail.exe.
    # Called from main.py after scraping completes.
    
    datestamp = date.today().strftime("%m-%d-%Y")
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"[mailer] Sending emails for {datestamp}...")

    news_ok = send_email(
        subject=f"Daily News: {datestamp}",
        body="Attached is Today's News Spreadsheet AND txt file (RealClearPolitics)",
        attachments=[
            os.path.join(script_dir, "RCPheadlines.txt"),
            os.path.join(script_dir, "RCPlinks.csv"),
        ],
    )

    jobs_ok = send_email(
        subject=f"Daily Jobs: {datestamp}",
        body="Attached is today's Craigslist job listings!",
        attachments=[
            os.path.join(script_dir, "jobs.txt"),
        ],
    )

    if news_ok and jobs_ok:
        print("[mailer] All emails sent successfully.")
    else:
        print("[mailer] One or more emails failed. Check output above.")


if __name__ == "__main__":
    send_all()
