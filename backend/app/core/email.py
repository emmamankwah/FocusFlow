import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

# Email helper for sending one-time verification codes to users.
def send_verification_email(to_email: str, otp: str):
    # Build the email message with a plain-text body and verification details.
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = to_email
    msg["Subject"] = "Your FocusFlow AI verification code"
    msg.attach(MIMEText(f"Your verification code is: {otp}\nExpires in 3 minutes.", "plain"))

    # Connect to the configured SMTP server and send the verification email.
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)