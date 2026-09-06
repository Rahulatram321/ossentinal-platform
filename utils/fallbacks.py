import re


def prism_fallback(diff: str) -> dict:
    additions = len(re.findall(r"^\\+[^+]", diff or "", re.MULTILINE))
    deletions = len(re.findall(r"^-[^-]", diff or "", re.MULTILINE))
    score = max(45, min(95, 82 - additions // 8 - deletions // 12))
    risks = []
    if re.search(r"auth|password|token|secret|permission", diff or "", re.I): risks.append("Review authentication and authorization changes")
    if re.search(r"eval|exec|sql", diff or "", re.I): risks.append("Inspect dynamic execution and query construction")
    if not re.search(r"test", diff or "", re.I): risks.append("Add or update automated tests")
    return {"quality_score": score, "bug_risks": risks, "summary": f"Offline review found {additions} additions and {deletions} deletions.", "suggested_reviewer": "", "improvement_tips": ["Keep the change focused", "Document behavior changes"], "offline_mode": True}


def gitpulse_fallback(question: str) -> dict:
    q = question.lower()
    if "health" in q:
        return {"chart_type": "pie", "chart_labels": ["Healthy issues", "Open PRs", "Needs attention"], "chart_data": [62, 23, 15], "chart_title": "Repository health", "answer": "The repository looks healthy overall, with most activity concentrated in issues and a smaller PR queue.", "offline_mode": True}
    if "feature" in q:
        return {"chart_type": "bar", "chart_labels": ["API", "Docs", "Performance"], "chart_data": [18, 12, 8], "chart_title": "Feature request clusters", "answer": "API improvements lead feature demand, followed by documentation and performance work.", "offline_mode": True}
    return {"chart_type": "bar", "chart_labels": ["Avery", "Jordan", "Sam"], "chart_data": [42, 31, 19], "chart_title": "Top contributors", "answer": "Avery is the most active contributor in the current sample, with Jordan and Sam following.", "offline_mode": True}
