import smtplib
from email.message import EmailMessage
import os

sender = os.getenv("GMAIL_USER")
receiver = "receiver@example.com"
password = os.getenv("GMAIL_APP_PASSWORD")

msg = EmailMessage()
msg["Subject"] = "Verification Email"
msg["From"] = sender
msg["To"] = receiver
msg.set_content("Hello! This email was sent using Python.")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender, password)
    server.send_message(msg)

print("Email sent successfully!")