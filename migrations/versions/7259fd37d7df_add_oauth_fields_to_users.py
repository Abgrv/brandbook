"""add oauth fields to users

Revision ID: 7259fd37d7df
Revises: 5b67950aba67
Create Date: 2025-08-23 21:07:11.085247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7259fd37d7df'
down_revision: Union[str, Sequence[str], None] = '5b67950aba67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(),
                    nullable=True)
    op.add_column('users', sa.Column('provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('provider_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.create_unique_constraint('uq_provider_providerid', 'users', ['provider', 'provider_id'])

def downgrade() -> None:
    op.drop_constraint('uq_provider_providerid', 'users', type_='unique')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'provider_id')
    op.drop_column('users', 'provider')
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(),
                    nullable=False)
