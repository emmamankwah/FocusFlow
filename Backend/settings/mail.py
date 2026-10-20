import smtplib
from email.message import EmailMessage
import os

from dotenv import load_dotenv

load_dotenv()  
sender = os.getenv("GMAIL_USER")
app_password = os.getenv("GMAIL_APP_PASSWORD")

msg =EmailMessage()
msg["Subject"] = "FocusFlow Test"
msg["From"] = sender
msg["To"] = "recipient@example.com"
msg.set_content("Welcome to FocusFlow!")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender, app_password)
    server.send_message(msg)