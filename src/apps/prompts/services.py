from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import Category, LLMProvider, Prompt


def list_categories(session: Session) -> list[Category]:
    return session.scalars(select(Category).order_by(Category.name)).all()


def list_providers(session: Session) -> list[LLMProvider]:
    return session.scalars(select(LLMProvider).order_by(LLMProvider.name)).all()


def list_approved_prompts(
    session: Session,
    *,
    page: int = 1,
    page_size: int = 12,
    search: str = "",
    category_ids: list[int] | None = None,
    provider_ids: list[int] | None = None,
) -> dict:
    query = (
        select(Prompt)
        .where(Prompt.is_approved.is_(True))
        .options(selectinload(Prompt.categories), selectinload(Prompt.providers))
    )

    if search:
        query = query.where(Prompt.title.ilike(f"%{search}%"))

    if category_ids:
        query = query.where(Prompt.categories.any(Category.id.in_(category_ids)))

    if provider_ids:
        query = query.where(Prompt.providers.any(LLMProvider.id.in_(provider_ids)))

    query = query.order_by(Prompt.updated_at.desc())

    offset = (page - 1) * page_size
    prompts = session.scalars(query.offset(offset).limit(page_size + 1)).all()

    has_next = len(prompts) > page_size
    prompts = prompts[:page_size]

    return {
        "prompts": [_serialize_prompt_card(p) for p in prompts],
        "has_next": has_next,
    }


def get_prompt_detail(session: Session, prompt_id: int) -> dict | None:
    prompt = session.scalars(
        select(Prompt)
        .where(Prompt.id == prompt_id, Prompt.is_approved.is_(True))
        .options(selectinload(Prompt.categories), selectinload(Prompt.providers))
    ).first()

    if prompt is None:
        return None

    return {
        "id": prompt.id,
        "title": prompt.title,
        "content": prompt.content,
        "author": prompt.author,
        "created_at": prompt.created_at.strftime("%d/%m/%Y"),
        "updated_at": prompt.updated_at.strftime("%d/%m/%Y"),
        "categories": [{"id": c.id, "name": c.name} for c in prompt.categories],
        "providers": [{"id": pr.id, "name": pr.name} for pr in prompt.providers],
    }


def create_prompt(
    session: Session,
    *,
    title: str,
    content: str,
    author: str,
    category_ids: list[int] | None = None,
    provider_ids: list[int] | None = None,
) -> Prompt:
    prompt = Prompt(title=title, content=content, author=author)

    if category_ids:
        cats = session.scalars(
            select(Category).where(Category.id.in_(category_ids))
        ).all()
        prompt.categories.extend(cats)

    if provider_ids:
        provs = session.scalars(
            select(LLMProvider).where(LLMProvider.id.in_(provider_ids))
        ).all()
        prompt.providers.extend(provs)

    session.add(prompt)
    session.commit()
    return prompt


def _truncate(text: str, word_count: int = 20) -> str:
    words = text.split()
    if len(words) <= word_count:
        return text
    return " ".join(words[:word_count]) + "..."


def _serialize_prompt_card(p: Prompt) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "preview": _truncate(p.content),
        "author": p.author,
        "updated_at": p.updated_at.strftime("%d/%m/%Y"),
        "categories": [{"id": c.id, "name": c.name} for c in p.categories],
        "providers": [{"id": pr.id, "name": pr.name} for pr in p.providers],
    }
