from agents.priority import calculate_priority
from agents.triage import classify_issue, process_issue
from agents.prism import parse_pr_url

def test_classifies_bug(): assert classify_issue("Crash on startup", "The app fails") == "bug"
def test_priority_is_urgent_for_security_failure(): assert calculate_priority("security", "critical auth vulnerability") ["level"] == "Urgent"
def test_triage_pipeline_returns_reply(): assert process_issue("o/r", 1, "Question", "How do I use this?")["reply"]
def test_parse_pr_url(): assert parse_pr_url("https://github.com/acme/project/pull/42") == ("acme", "project", 42)
