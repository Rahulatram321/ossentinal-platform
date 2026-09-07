import re
from datetime import datetime

LABEL_WEIGHTS = {"bug": 22, "feature": 10, "question": 6, "security": 36}
NEGATIVE_TERMS = {"blocked", "broken", "crash", "critical", "data loss", "fail", "frustrated", "urgent", "vulnerability"}
SECURITY_PATTERN = re.compile(r"auth|security|token|password|permission|exploit|cve", re.I)


def calculate_priority(label: str, text: str, age_days: int = 0, duplicate_similarity: float = 0.0) -> dict:
    score = 18 + LABEL_WEIGHTS.get(label, 6)
    score += min(20, age_days // 2)
    score += min(18, duplicate_similarity * 18)
    if any(term in text.lower() for term in NEGATIVE_TERMS): score += 14
    if SECURITY_PATTERN.search(text): score += 12
    score = max(0, min(100, int(score)))
    level = "Urgent" if score >= 80 else "High" if score >= 60 else "Normal" if score >= 40 else "Low"
    return {"score": score, "level": level}


# Explicit name used by the triage pipeline and integrations.
calculate_priority_score = calculate_priority
