FROM python:3.11-slim AS builder
WORKDIR /build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt .
RUN python -m venv /venv && /venv/bin/pip install --upgrade pip && /venv/bin/pip install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
ENV PATH="/venv/bin:$PATH" PYTHONUNBUFFERED=1
COPY --from=builder /venv /venv
COPY . .
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "app.main:app", "--bind", "0.0.0.0:8000"]
