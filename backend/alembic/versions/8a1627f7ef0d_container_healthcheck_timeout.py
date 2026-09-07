"""container_healthcheck_timeout

Revision ID: 8a1627f7ef0d
Revises: 7ef482012b0a
Create Date: 2026-09-07 02:11:50.127500

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a1627f7ef0d"
down_revision: str | Sequence[str] | None = "7ef482012b0a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("containers") as batch_op:
        batch_op.add_column(
            sa.Column("healthcheck_timeout", sa.Integer(), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("containers") as batch_op:
        batch_op.drop_column("healthcheck_timeout")
