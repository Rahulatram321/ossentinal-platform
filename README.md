# OSSentinel AI

OSSentinel is a FastAPI SaaS platform for open-source maintainers. It combines issue triage, pull-request review, repository analytics, and weekly reporting in one GitHub-focused workspace.

## Run locally

1. Create an environment: `python -m venv .venv` and activate it.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set a strong `SESSION_SECRET`.
4. Start the app: `uvicorn app.main:app --reload`.
5. Open `http://localhost:8000/home`, then choose **Try the live demo**.

Demo mode is deterministic and works without external credentials. Add `GEMINI_API_KEY`, `GITHUB_TOKEN`, and OAuth values to enable live integrations.

## Render deployment

1. Create a Web Service from this repository.
2. Use `render.yaml`, or build with `pip install -r requirements.txt` and start with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Production foundation

The `app/` package is the production application boundary. It introduces an app factory, typed settings, services, schemas, versioned prompts, Alembic, and Celery/Redis wiring while the legacy MVP routes are migrated incrementally. For a local production-like stack, copy `.env.local.example` to `.env.local` and run `docker compose -f docker/docker-compose.yml up --build`.
3. Add production variables, especially `SESSION_SECRET`, `DATABASE_URL`, GitHub OAuth values, and `GITHUB_WEBHOOK_SECRET`.

## GitHub App setup

1. Create a GitHub App with Issues, Pull requests, Contents, and Metadata permissions.
2. Set the callback URL to `{BASE_URL}/auth/callback` and webhook URL to `{BASE_URL}/webhook`.
3. Generate a webhook secret and configure `GITHUB_WEBHOOK_SECRET`.
4. Configure OAuth and token variables, then install the App on a test repository.

## Quality checks

```text
python -m compileall -q core agents utils github routers main.py
pytest -q
```
