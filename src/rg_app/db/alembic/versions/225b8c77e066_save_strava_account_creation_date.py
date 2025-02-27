"""Save strava account creation date

Revision ID: 225b8c77e066
Revises: 5ee33b93abdb
Create Date: 2025-02-25 21:25:35.607602

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

import rg_app.db.decorators

# revision identifiers, used by Alembic.
revision: str = "225b8c77e066"
down_revision: Union[str, None] = "5ee33b93abdb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column(
            "strava_account_created_at",
            rg_app.db.decorators.UTCDateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "strava_account_created_at")
    # ### end Alembic commands ###
