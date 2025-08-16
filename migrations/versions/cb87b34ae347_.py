"""empty message

Revision ID: cb87b34ae347
Revises: 243ad642a294
Create Date: 2025-08-13 21:27:49.615760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb87b34ae347'
down_revision: Union[str, Sequence[str], None] = '243ad642a294'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
