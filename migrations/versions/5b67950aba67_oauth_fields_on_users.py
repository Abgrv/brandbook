"""oauth fields on users

Revision ID: 5b67950aba67
Revises: 46ed4b0c54a1
Create Date: 2025-08-22 12:22:30.026320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b67950aba67'
down_revision: Union[str, Sequence[str], None] = '46ed4b0c54a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
