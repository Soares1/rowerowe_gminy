"""Add capacity to store all activities

Revision ID: b00b80ec0f51
Revises: 225b8c77e066
Create Date: 2025-03-25 20:21:59.930891

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

import rg_app.db.decorators

# revision identifiers, used by Alembic.
revision: str = "b00b80ec0f51"
down_revision: Union[str, None] = "225b8c77e066"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ineligible_activity",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("reject_reason", sa.String(length=20), nullable=False),
        sa.Column("start", rg_app.db.decorators.UTCDateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("activity", sa.Column("full_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("activity", "full_data")
    op.drop_table("ineligible_activity")
    # ### end Alembic commands ###
