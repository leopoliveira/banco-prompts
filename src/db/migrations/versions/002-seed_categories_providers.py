"""seed categories and providers

Revision ID: 002
Revises: 001
Create Date: 2026-04-01 17:30:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

categories_table = sa.table(
    "categories",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

llm_providers_table = sa.table(
    "llm_providers",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

CATEGORIES = [
    "Escrita",
    "Programacao",
    "Marketing",
    "Educacao",
    "Analise de Dados",
    "Traducao",
    "Resumo",
    "Criatividade",
]

PROVIDERS = [
    "ChatGPT",
    "Claude",
    "Gemini",
    "Perplexity",
    "DeepSeek",
    "Copilot",
    "Grok",
    "LLaMA",
]


def upgrade() -> None:
    op.bulk_insert(
        categories_table,
        [{"name": name} for name in CATEGORIES],
    )
    op.bulk_insert(
        llm_providers_table,
        [{"name": name} for name in PROVIDERS],
    )


def downgrade() -> None:
    op.execute(
        categories_table.delete().where(
            categories_table.c.name.in_(CATEGORIES)
        )
    )
    op.execute(
        llm_providers_table.delete().where(
            llm_providers_table.c.name.in_(PROVIDERS)
        )
    )
