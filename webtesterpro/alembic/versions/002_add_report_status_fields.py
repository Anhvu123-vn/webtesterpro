"""002 — Thêm status, modules_run, results_json vào bảng reports."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("reports") as batch_op:
        batch_op.add_column(sa.Column("status", sa.String(length=20), nullable=False, server_default="completed"))
        batch_op.add_column(sa.Column("modules_run", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("results_json", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("reports") as batch_op:
        batch_op.drop_column("results_json")
        batch_op.drop_column("modules_run")
        batch_op.drop_column("status")
