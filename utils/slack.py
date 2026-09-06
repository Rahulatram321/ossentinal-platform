import httpx
from core.config import settings

async def send_slack(webhook_url: str, blocks: list) -> bool:
    try:
        response = await httpx.AsyncClient(timeout=5).post(webhook_url, json={"blocks": blocks}); return response.is_success
    except Exception: return False

def triage_blocks(repo, issue_num, title, label, priority):
    return [{"type": "header", "text": {"type": "plain_text", "text": "OSSentinel triaged an issue"}}, {"type": "section", "text": {"type": "mrkdwn", "text": f"*{repo}* issue #{issue_num}: {title}\\nLabel: `{label}` | Priority: `{priority}`"}}]

def prism_blocks(repo, pr_num, score, risks_count): return [{"type": "section", "text": {"type": "mrkdwn", "text": f"PR #{pr_num} in {repo}: {score}/100, {risks_count} risks"}}]
