import smtplib
from email.message import EmailMessage
from core.config import settings


def send_weekly_digest(to: str, repo: str, report_md: str) -> bool:
    """Send a plain-text digest; return False rather than breaking a report job."""
    if not to or not settings.smtp_user or not settings.smtp_pass:
        return False
    message = EmailMessage()
    message["Subject"] = f"OSSentinel weekly report: {repo}"
    message["From"] = settings.smtp_user
    message["To"] = to
    message.set_content(report_md)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_pass)
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException):
        return False
