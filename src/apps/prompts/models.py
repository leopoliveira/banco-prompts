from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

prompt_categories = Table(
    "prompt_categories",
    Base.metadata,
    Column("prompt_id", Integer, ForeignKey("prompts.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)

prompt_llm_providers = Table(
    "prompt_llm_providers",
    Base.metadata,
    Column("prompt_id", Integer, ForeignKey("prompts.id"), primary_key=True),
    Column(
        "llm_provider_id", Integer, ForeignKey("llm_providers.id"), primary_key=True
    ),
)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class LLMProvider(Base):
    __tablename__ = "llm_providers"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(100))
    is_approved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    categories: Mapped[list["Category"]] = relationship(
        secondary=prompt_categories, init=False, default_factory=list
    )
    providers: Mapped[list["LLMProvider"]] = relationship(
        secondary=prompt_llm_providers, init=False, default_factory=list
    )
