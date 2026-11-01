"""Create persistent project lifecycle tables.

Revision ID: 20261102_0001
Revises:
Create Date: 2026-11-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20261102_0001"
down_revision = None
branch_labels = None
depends_on = None


site_spec_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("site_type", sa.String(length=24), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("current_version_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("site_type IN ('portfolio', 'restaurant', 'other')", name="ck_projects_site_type"),
        sa.CheckConstraint("status IN ('active', 'archived')", name="ck_projects_status"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "slug", name="uq_projects_workspace_slug"),
    )
    op.create_index("ix_projects_workspace_id", "projects", ["workspace_id"])
    op.create_index("ix_projects_workspace_updated", "projects", ["workspace_id", "updated_at"])

    op.create_table(
        "project_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("site_spec", site_spec_type, nullable=False),
        sa.Column("change_description", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "version_number", name="uq_project_versions_number"),
    )
    op.create_index("ix_project_versions_project_id", "project_versions", ["project_id"])
    op.create_index("ix_project_versions_project_created", "project_versions", ["project_id", "created_at"])
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("projects") as batch_op:
            batch_op.create_foreign_key(
                "fk_projects_current_version", "project_versions", ["current_version_id"], ["id"], ondelete="SET NULL"
            )
    else:
        op.create_foreign_key(
            "fk_projects_current_version",
            "projects",
            "project_versions",
            ["current_version_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_table(
        "generation_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("resulting_version_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("generation_mode", sa.String(length=24), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('running', 'completed', 'failed')", name="ck_generation_runs_status"),
        sa.CheckConstraint("generation_mode IN ('create', 'generate', 'restore')", name="ck_generation_runs_mode"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resulting_version_id"], ["project_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generation_runs_project_id", "generation_runs", ["project_id"])
    op.create_index("ix_generation_runs_project_created", "generation_runs", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_generation_runs_project_created", table_name="generation_runs")
    op.drop_index("ix_generation_runs_project_id", table_name="generation_runs")
    op.drop_table("generation_runs")
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("projects") as batch_op:
            batch_op.drop_constraint("fk_projects_current_version", type_="foreignkey")
    else:
        op.drop_constraint("fk_projects_current_version", "projects", type_="foreignkey")
    op.drop_index("ix_project_versions_project_created", table_name="project_versions")
    op.drop_index("ix_project_versions_project_id", table_name="project_versions")
    op.drop_table("project_versions")
    op.drop_index("ix_projects_workspace_updated", table_name="projects")
    op.drop_index("ix_projects_workspace_id", table_name="projects")
    op.drop_table("projects")
