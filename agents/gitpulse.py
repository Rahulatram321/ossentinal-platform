import re
from core.config import settings
from agents.fallbacks import gitpulse_fallback


def fetch_repo_data(repo_name: str, token: str = "") -> str:
    return f"REPO INFO: {repo_name} | Stars: 0 | Forks: 0 | Open Issues: 0 | Language: Unknown"


def query_gemini(question: str, context: str) -> dict:
    if not settings.gemini_api_key:
        return gitpulse_fallback(question)
    prompt = f"""Use this repository context to answer the question. Use exactly this format:\nCHART_TYPE: bar|line|pie|none\nCHART_LABELS: label1|label2\nCHART_DATA: 1|2\nANSWER: concise answer\n\nCONTEXT: {context[:6000]}\nQUESTION: {question}"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        text = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text
        fields = dict((key.upper(), value.strip()) for key, value in re.findall(r"^(CHART_TYPE|CHART_LABELS|CHART_DATA|ANSWER)\s*:\s*(.+)$", text, re.M | re.I))
        chart_type = fields.get("CHART_TYPE", "none").lower()
        if chart_type not in {"bar", "line", "pie", "none"}:
            chart_type = "none"
        labels = [item.strip() for item in fields.get("CHART_LABELS", "").split("|") if item.strip()]
        data = [float(item.strip()) for item in fields.get("CHART_DATA", "").split("|") if item.strip()]
        answer = fields.get("ANSWER", "").strip()
        if not answer or (chart_type != "none" and len(labels) != len(data)):
            raise ValueError("Invalid Gemini GitPulse response")
        return {"chart_type": chart_type, "chart_labels": labels, "chart_data": data, "chart_title": "Repository insight", "answer": answer, "offline_mode": False}
    except Exception:
        return gitpulse_fallback(question)


def answer_query(question: str, repo_name: str, token: str = "") -> dict:
    try: return query_gemini(question, fetch_repo_data(repo_name, token))
    except Exception: return gitpulse_fallback(question)
