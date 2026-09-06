import json
from pathlib import Path

_QUEUE = Path(".osssentinel-queue.json")

def enqueue(task: dict) -> None:
    rows = json.loads(_QUEUE.read_text()) if _QUEUE.exists() else []
    rows.append({"status": "pending", "task": task}); _QUEUE.write_text(json.dumps(rows))

def pending() -> list[dict]:
    return json.loads(_QUEUE.read_text()) if _QUEUE.exists() else []

def recover_pending_webhook_tasks() -> list[dict]: return pending()
