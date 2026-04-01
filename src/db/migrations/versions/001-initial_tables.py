"""initial tables

Revision ID: 001
Revises:
Create Date: 2026-04-01 17:09:21.167779
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('llm_providers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('prompts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('author', sa.String(length=100), nullable=False),
    sa.Column('is_approved', sa.Boolean(), nullable=False),
    sa.Column(
        'created_at', sa.DateTime(),
        server_default=sa.text('now()'), nullable=False,
    ),
    sa.Column(
        'updated_at', sa.DateTime(),
        server_default=sa.text('now()'), nullable=False,
    ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prompt_categories',
    sa.Column('prompt_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ),
    sa.PrimaryKeyConstraint('prompt_id', 'category_id')
    )
    op.create_table('prompt_llm_providers',
    sa.Column('prompt_id', sa.Integer(), nullable=False),
    sa.Column('llm_provider_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['llm_provider_id'], ['llm_providers.id'], ),
    sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ),
    sa.PrimaryKeyConstraint('prompt_id', 'llm_provider_id')
    )


def downgrade() -> None:
    op.drop_table('prompt_llm_providers')
    op.drop_table('prompt_categories')
    op.drop_table('prompts')
    op.drop_table('llm_providers')
    op.drop_table('categories')
