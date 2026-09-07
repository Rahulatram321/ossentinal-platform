"""Load versioned AI prompts from the canonical application prompt directory."""
from pathlib import Path

PROMPT_DIRECTORY = Path(__file__).resolve().parents[1] / "app" / "prompts"


def render_prompt(name: str, **values: str) -> str:
    return (PROMPT_DIRECTORY / name).read_text(encoding="utf-8").format(**values)
