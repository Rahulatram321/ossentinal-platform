import hashlib, hmac, json
from core.config import settings


def validate_signature(body: bytes, signature: str | None) -> bool:
    if not settings.github_webhook_secret: return True
    expected = "sha256=" + hmac.new(settings.github_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    return bool(signature and hmac.compare_digest(expected, signature))


def parse_payload(body: bytes) -> dict: return json.loads(body)
