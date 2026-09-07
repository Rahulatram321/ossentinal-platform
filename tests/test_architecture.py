from app.config import settings
from app.main import create_app
from utils.prompts import render_prompt


def test_application_factory_uses_production_metadata():
    application = create_app()
    assert application.title == settings.app_name
    assert application.version == "3.0.0"


def test_triage_prompt_is_versioned():
    prompt = render_prompt("triage_classification.txt", title="Crash", body="Broken")
    assert "Classify this GitHub issue" in prompt
    assert "Crash" in prompt
