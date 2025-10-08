"""add plaid_account_id to accounts

Revision ID: 3662287a8bc6
Revises: de5d2bc61845
Create Date: 2025-10-07 20:12:58.278332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3662287a8bc6'
down_revision: Union[str, Sequence[str], None] = 'de5d2bc61845'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("plaid_account_id", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.drop_column("plaid_account_id")
