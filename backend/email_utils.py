"""
email_utils.py
--------------
Sends password reset emails via Gmail SMTP. Same as the Streamlit
version, except the reset link now points at the frontend's HTML
page instead of a Streamlit query param.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5500")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_reset_email(to_email: str, reset_token: str):
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set in .env to send emails.")

    reset_link = f"{FRONTEND_BASE_URL}/login?reset_token={reset_token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset your Study Planner password"
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_email

    text_body = f"""
Hi,

We received a request to reset your Study Planner password.

Click this link to set a new password (valid for 30 minutes):
{reset_link}

If you didn't request this, you can safely ignore this email.
"""
    message.attach(MIMEText(text_body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, to_email, message.as_string())