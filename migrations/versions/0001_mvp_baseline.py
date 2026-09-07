"""Create the existing MVP schema under Alembic control.

Revision ID: 0001_mvp_baseline
Revises: None
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_mvp_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("github_id", sa.String(100), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("email", sa.String(255), nullable=False, server_default=""),
        sa.Column("plan", sa.String(30), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("github_id"),
    )
    op.create_index("ix_users_github_id", "users", ["github_id"])
    op.create_table("connected_repos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_github_id", sa.String(100), sa.ForeignKey("users.github_id"), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("webhook_status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("total_triaged", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_reviewed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_queries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("connected_at", sa.DateTime(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_connected_repos_owner_github_id", "connected_repos", ["owner_github_id"])
    op.create_index("ix_connected_repos_full_name", "connected_repos", ["full_name"])
    op.create_table("triage_logs",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("repo_full_name", sa.String(255), nullable=False),
        sa.Column("issue_number", sa.Integer(), nullable=False), sa.Column("issue_title", sa.String(500), nullable=False),
        sa.Column("label", sa.String(30), nullable=False), sa.Column("priority_score", sa.Integer(), nullable=False),
        sa.Column("priority_level", sa.String(30), nullable=False), sa.Column("duplicate_warning", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.8"), sa.Column("ai_reply_preview", sa.String(200), nullable=False, server_default=""),
        sa.Column("status", sa.String(30), nullable=False, server_default="to_triage"), sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_triage_logs_repo_full_name", "triage_logs", ["repo_full_name"])
    op.create_table("pr_reviews",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("repo_full_name", sa.String(255), nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=False, server_default="0"), sa.Column("pr_url", sa.String(500), nullable=False),
        sa.Column("quality_score", sa.Integer(), nullable=False), sa.Column("bug_risk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary_preview", sa.String(500), nullable=False, server_default=""), sa.Column("suggested_reviewer", sa.String(100), nullable=False, server_default=""),
        sa.Column("offline_mode", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table("gitpulse_queries",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("repo_full_name", sa.String(255), nullable=False),
        sa.Column("question", sa.Text(), nullable=False), sa.Column("answer_preview", sa.String(500), nullable=False, server_default=""),
        sa.Column("chart_type", sa.String(20), nullable=False, server_default="none"), sa.Column("offline_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table("weekly_reports",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("repo_full_name", sa.String(255), nullable=False),
        sa.Column("report_markdown", sa.Text(), nullable=False), sa.Column("triaged_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reviewed_count", sa.Integer(), nullable=False, server_default="0"), sa.Column("urgent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
    )
    op.create_table("activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("github_username", sa.String(100), nullable=False, server_default="demo"),
        sa.Column("module", sa.String(30), nullable=False), sa.Column("action", sa.String(255), nullable=False),
        sa.Column("repo_full_name", sa.String(255), nullable=False, server_default=""), sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("weekly_reports")
    op.drop_table("gitpulse_queries")
    op.drop_table("pr_reviews")
    op.drop_index("ix_triage_logs_repo_full_name", table_name="triage_logs")
    op.drop_table("triage_logs")
    op.drop_index("ix_connected_repos_full_name", table_name="connected_repos")
    op.drop_index("ix_connected_repos_owner_github_id", table_name="connected_repos")
    op.drop_table("connected_repos")
    op.drop_index("ix_users_github_id", table_name="users")
    op.drop_table("users")
