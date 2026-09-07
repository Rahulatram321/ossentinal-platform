import hashlib
import math
from typing import Iterable
from core.config import settings

_embedding_cache: dict[str, list[float]] = {}


def _local_embedding(text: str) -> list[float]:
    key = hashlib.sha256(text.encode()).hexdigest()
    if key not in _embedding_cache:
        values = [0.0] * 32
        for index, char in enumerate(text.lower()): values[index % 32] += ord(char) / 255
        norm = math.sqrt(sum(value * value for value in values)) or 1
        _embedding_cache[key] = [value / norm for value in values]
    return _embedding_cache[key]


def _embedding(text: str) -> list[float]:
    """Use Gemini's requested embedding model, falling back deterministically offline."""
    if not settings.gemini_api_key:
        return _local_embedding(text)
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        values = genai.embed_content(model="models/text-embedding-004", content=text, task_type="semantic_similarity")["embedding"]
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]
    except Exception:
        return _local_embedding(text)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def find_duplicate(text: str, open_issues: Iterable[dict] = ()) -> dict:
    best = {"is_duplicate": False, "similarity": 0.0, "issue_number": None}
    current = _embedding(text)
    for issue in list(open_issues)[:30]:
        similarity = cosine_similarity(current, _embedding(f"{issue.get('title', '')} {issue.get('body', '')}"))
        if similarity > best["similarity"]: best = {"is_duplicate": similarity > 0.85, "similarity": similarity, "issue_number": issue.get("number")}
    return best
