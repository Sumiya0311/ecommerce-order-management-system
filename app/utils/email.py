import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv ("SMTP_USERNAME")
    smtp_password = os.getenv ("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)

    if not smtp_host or not smtp_username or not smtp_password:
        logger.error("SMTP configuration is missing")
        return

    try:
        message = MIMEMultipart()
        message["From"] = smtp_from_email
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(
                smtp_from_email,
                to_email,
                message.as_string()
            )

        logger.info("Email sent successfully to %s", to_email)

    except Exception:
        logger.exception("Failed to send email to %s", to_email)