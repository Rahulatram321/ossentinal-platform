from core.config import settings

def send_weekly_digest(to: str, repo: str, report_md: str) -> bool:
    if not to or not settings.smtp_user: return False
    return False
