"""empty message

Revision ID: 46ed4b0c54a1
Revises: cb87b34ae347
Create Date: 2025-08-13 22:07:24.560647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46ed4b0c54a1'
down_revision: Union[str, Sequence[str], None] = 'cb87b34ae347'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
