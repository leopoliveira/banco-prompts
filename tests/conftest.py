import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import apps.prompts.models  # noqa: F401
from apps.prompts.models import Category, LLMProvider, Prompt
from db.base import Base


@pytest.fixture(scope="session")
def db_engine():
    from django.conf import settings

    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(autouse=True)
def _patch_session(db_session, monkeypatch):
    monkeypatch.setattr(
        "db.engine.SessionLocal",
        lambda: db_session,
    )


@pytest.fixture
def sample_category(db_session):
    cat = Category(name="Escrita")
    db_session.add(cat)
    db_session.flush()
    return cat


@pytest.fixture
def sample_provider(db_session):
    prov = LLMProvider(name="ChatGPT")
    db_session.add(prov)
    db_session.flush()
    return prov


@pytest.fixture
def sample_prompt(db_session, sample_category, sample_provider):
    prompt = Prompt(
        title="Prompt de Teste",
        content=(
            "Este e um conteudo de teste com mais de vinte"
            " palavras para que possamos verificar que o"
            " truncamento esta funcionando corretamente no"
            " preview do card na pagina principal do aplicativo"
        ),
        author="Testador",
        is_approved=True,
    )
    prompt.categories.append(sample_category)
    prompt.providers.append(sample_provider)
    db_session.add(prompt)
    db_session.flush()
    return prompt


@pytest.fixture
def unapproved_prompt(db_session):
    prompt = Prompt(
        title="Prompt Pendente",
        content="Conteudo pendente de aprovacao",
        author="Autor Pendente",
        is_approved=False,
    )
    db_session.add(prompt)
    db_session.flush()
    return prompt
