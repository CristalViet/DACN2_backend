"""create users table

Revision ID: 76366edb1115
Revises: c5670f986e56
Create Date: 2025-11-14 21:04:47.988977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76366edb1115'
down_revision: Union[str, None] = 'c5670f986e56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
