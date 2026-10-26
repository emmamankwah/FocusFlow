import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import logging

logging = logging.getLogger(__name__)
load_dotenv()

def configure_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends an email using Gmail SMTP SSL.
    Returns True if successful, False otherwise.
    """
    sender = os.getenv("GMAIL_USER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    app_port = os.getenv("SMTP_PORT") 

    if not sender or not app_password or not app_port:
        raise ValueError("Missing Credentials in Server.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(app_port) as server:
            server.login(sender, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        logging.error("Failed to send email ")
        return False