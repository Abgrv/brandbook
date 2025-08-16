"""create users and brandbooks tables

Revision ID: 243ad642a294
Revises: 
Create Date: 2025-08-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '243ad642a294'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # создаём таблицу users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )

    # создаём таблицу brandbooks
    op.create_table(
        'brandbooks',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )


def downgrade():
    op.drop_table('brandbooks')
    op.drop_table('users')
