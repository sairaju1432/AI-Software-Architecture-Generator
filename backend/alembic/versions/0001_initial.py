"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-01
"""
from alembic import op
import sqlalchemy as sa
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    plan = sa.Enum("free", "pro", name="plan")
    status = sa.Enum("queued", "running", "completed", "failed", name="generationstatus")
    plan.create(op.get_bind(), checkfirst=True); status.create(op.get_bind(), checkfirst=True)
    op.create_table("users", sa.Column("id", sa.String(), primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("hashed_password", sa.String()), sa.Column("full_name", sa.String(160), nullable=False), sa.Column("google_sub", sa.String(), unique=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("projects", sa.Column("id", sa.String(), primary_key=True), sa.Column("user_id", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(180), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_projects_user_id", "projects", ["user_id"])
    op.create_table("subscriptions", sa.Column("id", sa.String(), primary_key=True), sa.Column("user_id", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("plan", plan, nullable=False), sa.Column("stripe_customer_id", sa.String()), sa.Column("stripe_subscription_id", sa.String()), sa.Column("monthly_generation_count", sa.Integer(), nullable=False), sa.Column("current_period_start", sa.DateTime(), nullable=False), sa.UniqueConstraint("user_id"))
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_table("generations", sa.Column("id", sa.String(), primary_key=True), sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False), sa.Column("prompt", sa.Text(), nullable=False), sa.Column("status", status, nullable=False), sa.Column("error", sa.Text()), sa.Column("tokens_used", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("completed_at", sa.DateTime()))
    op.create_index("ix_generations_project_id", "generations", ["project_id"])
    op.create_table("architecture_outputs", sa.Column("id", sa.String(), primary_key=True), sa.Column("generation_id", sa.String(), sa.ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, unique=True), *[sa.Column(c, sa.JSON(), nullable=False) for c in ["functional_requirements","non_functional_requirements","recommended_architecture","microservices","database_schema","rest_api_design","folder_structure","cicd_strategy","docker_configuration","kubernetes_plan","aws_recommendation","cost_estimation","mermaid_diagrams","raw"]])

def downgrade():
    op.drop_table("architecture_outputs"); op.drop_index("ix_generations_project_id", table_name="generations"); op.drop_table("generations"); op.drop_index("ix_subscriptions_user_id", table_name="subscriptions"); op.drop_table("subscriptions"); op.drop_index("ix_projects_user_id", table_name="projects"); op.drop_table("projects"); op.drop_index("ix_users_email", table_name="users"); op.drop_table("users"); sa.Enum(name="generationstatus").drop(op.get_bind(), checkfirst=True); sa.Enum(name="plan").drop(op.get_bind(), checkfirst=True)
