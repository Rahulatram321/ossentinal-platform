"""Canonical, typed runtime configuration for every deployment."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "OSSentinel AI"
    base_url: str = "http://localhost:8000"
    session_secret: str = "change-this-in-production"
    session_https_only: bool = False
    session_samesite: str = "lax"
    trusted_hosts: str = "localhost,127.0.0.1"
    cors_allow_origins: str = "http://localhost:8000"
    database_url: str = "sqlite:///./osssentinel.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    gemini_api_key: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    github_oauth_scope: str = "read:user,public_repo"
    github_token: str = ""
    github_webhook_secret: str = ""
    github_app_id: str = ""
    github_app_private_key_path: str = ""
    feature_triage: bool = True
    feature_prism: bool = True
    feature_gitpulse: bool = True
    feature_reports: bool = True
    feature_slack: bool = False
    feature_email: bool = False
    allow_demo_login: bool = True
    allow_env_token_auth: bool = False
    triage_limit_free: int = 100
    prism_limit_free: int = 10
    gitpulse_limit_free: int = 5
    slack_webhook_url: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    digest_to_email: str = ""
    log_level: str = "INFO"
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def trusted_host_list(self) -> list[str]:
        return [value.strip() for value in self.trusted_hosts.split(",") if value.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [value.strip() for value in self.cors_allow_origins.split(",") if value.strip()]


settings = Settings()
