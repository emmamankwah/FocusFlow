import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

APP_NAME = os.getenv("APP_NAME", "FocusFlow")
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "") or APP_NAME
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_TIMEOUT_SECONDS = int(os.getenv("SMTP_TIMEOUT_SECONDS", "15"))

logger = logging.getLogger(__name__)


def configure_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email through Gmail SMTP using TLS.

    Returns ``True`` on success and ``False`` when the SMTP server rejects the
    message. Missing configuration raises ``ValueError`` so the caller can
    report a setup problem instead of a delivery failure.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise ValueError("Missing Gmail credentials (GMAIL_USER/GMAIL_APP_PASSWORD).")
    if not SMTP_HOST:
        raise ValueError("Missing SMTP settings (SMTP_HOST/SMTP_PORT).")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{MAIL_FROM_NAME} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        if SMTP_PORT == 465:
            # Implicit TLS (Gmail's SMTPS port).
            server = smtplib.SMTP_SSL(
                SMTP_HOST,
                SMTP_PORT,
                timeout=SMTP_TIMEOUT_SECONDS,
                context=context,
            )
        else:
            # Port 587 and friends upgrade a plain connection with STARTTLS.
            server = smtplib.SMTP(
                SMTP_HOST,
                SMTP_PORT,
                timeout=SMTP_TIMEOUT_SECONDS,
            )

        with server:
            if SMTP_PORT != 465:
                server.starttls(context=context)
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False