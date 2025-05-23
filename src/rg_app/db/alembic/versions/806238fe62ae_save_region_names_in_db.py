"""save region names in db

Revision ID: 806238fe62ae
Revises: 23c757641f3f
Create Date: 2025-04-06 20:50:44.255980

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "806238fe62ae"
down_revision: Union[str, None] = "23c757641f3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("region", sa.Column("name", sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("region", "name")
    # ### end Alembic commands ###
