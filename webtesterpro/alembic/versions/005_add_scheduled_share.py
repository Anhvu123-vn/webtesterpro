"""005 — Thêm bảng scheduled_tests và share_tokens."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Scheduled tests table
    op.create_table(
        "scheduled_tests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("modules", sa.Text(), nullable=False),
        sa.Column("cron_expression", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("last_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scheduled_tests_id"), "scheduled_tests", ["id"], unique=False)
    op.create_index(op.f("ix_scheduled_tests_user_id"), "scheduled_tests", ["user_id"], unique=False)

    # Share tokens table
    op.create_table(
        "share_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_share_tokens_id"), "share_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_share_tokens_token"), "share_tokens", ["token"], unique=True)
    op.create_index(op.f("ix_share_tokens_report_id"), "share_tokens", ["report_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_share_tokens_report_id"), table_name="share_tokens")
    op.drop_index(op.f("ix_share_tokens_token"), table_name="share_tokens")
    op.drop_index(op.f("ix_share_tokens_id"), table_name="share_tokens")
    op.drop_table("share_tokens")

    op.drop_index(op.f("ix_scheduled_tests_user_id"), table_name="scheduled_tests")
    op.drop_index(op.f("ix_scheduled_tests_id"), table_name="scheduled_tests")
    op.drop_table("scheduled_tests")
