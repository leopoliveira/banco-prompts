import json

from django.test import Client

from apps.prompts.models import Category, LLMProvider, Prompt


class TestModels:
    def test_create_category(self, db_session):
        cat = Category(name="Programacao")
        db_session.add(cat)
        db_session.flush()
        assert cat.id is not None
        assert cat.name == "Programacao"

    def test_create_llm_provider(self, db_session):
        prov = LLMProvider(name="Claude")
        db_session.add(prov)
        db_session.flush()
        assert prov.id is not None
        assert prov.name == "Claude"

    def test_create_prompt(self, db_session):
        prompt = Prompt(title="Teste", content="Conteudo", author="Autor")
        db_session.add(prompt)
        db_session.flush()
        assert prompt.id is not None
        assert prompt.is_approved is False

    def test_prompt_categories_relationship(self, db_session, sample_prompt):
        assert len(sample_prompt.categories) == 1
        assert sample_prompt.categories[0].name == "Escrita"

    def test_prompt_providers_relationship(self, db_session, sample_prompt):
        assert len(sample_prompt.providers) == 1
        assert sample_prompt.providers[0].name == "ChatGPT"


class TestIndexView:
    def test_index_returns_200(self):
        client = Client()
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_title(self):
        client = Client()
        response = client.get("/")
        assert "Banco de Prompts de IA" in response.content.decode()


class TestPromptListAPI:
    def test_returns_only_approved(self, sample_prompt, unapproved_prompt):
        client = Client()
        response = client.get("/api/prompts/")
        data = json.loads(response.content)
        titles = [p["title"] for p in data["prompts"]]
        assert "Prompt de Teste" in titles
        assert "Prompt Pendente" not in titles

    def test_pagination(self, db_session, sample_category):
        for i in range(15):
            p = Prompt(
                title=f"Prompt {i}",
                content=f"Conteudo {i}",
                author="Autor",
                is_approved=True,
            )
            db_session.add(p)
        db_session.flush()

        client = Client()
        response = client.get("/api/prompts/?page_size=10")
        data = json.loads(response.content)
        assert len(data["prompts"]) == 10
        assert data["has_next"] is True

        response = client.get("/api/prompts/?page=2&page_size=10")
        data = json.loads(response.content)
        assert len(data["prompts"]) == 5
        assert data["has_next"] is False

    def test_search_by_title(self, sample_prompt):
        client = Client()
        response = client.get("/api/prompts/?search=Teste")
        data = json.loads(response.content)
        assert len(data["prompts"]) >= 1
        assert data["prompts"][0]["title"] == "Prompt de Teste"

    def test_filter_by_category(self, sample_prompt, sample_category):
        client = Client()
        response = client.get(f"/api/prompts/?categories={sample_category.id}")
        data = json.loads(response.content)
        assert len(data["prompts"]) >= 1

    def test_filter_by_provider(self, sample_prompt, sample_provider):
        client = Client()
        response = client.get(f"/api/prompts/?providers={sample_provider.id}")
        data = json.loads(response.content)
        assert len(data["prompts"]) >= 1

    def test_preview_truncation(self, sample_prompt):
        client = Client()
        response = client.get("/api/prompts/")
        data = json.loads(response.content)
        preview = data["prompts"][0]["preview"]
        assert preview.endswith("...")
        assert len(preview.split()) <= 21  # 20 words + "..."

    def test_empty_result(self):
        client = Client()
        response = client.get("/api/prompts/?search=inexistente999")
        data = json.loads(response.content)
        assert data["prompts"] == []
        assert data["has_next"] is False


class TestPromptDetailAPI:
    def test_returns_approved_prompt(self, sample_prompt):
        client = Client()
        response = client.get(f"/api/prompts/{sample_prompt.id}/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["title"] == "Prompt de Teste"
        assert "content" in data

    def test_returns_404_for_unapproved(self, unapproved_prompt):
        client = Client()
        response = client.get(f"/api/prompts/{unapproved_prompt.id}/")
        assert response.status_code == 404

    def test_returns_404_for_nonexistent(self):
        client = Client()
        response = client.get("/api/prompts/99999/")
        assert response.status_code == 404


class TestSubmitView:
    def test_get_renders_form(self):
        client = Client()
        response = client.get("/enviar/")
        assert response.status_code == 200
        assert "Enviar Prompt" in response.content.decode()

    def test_post_creates_unapproved_prompt(
        self, db_session, sample_category, sample_provider
    ):
        client = Client()
        response = client.post(
            "/enviar/",
            {
                "title": "Novo Prompt",
                "content": "Conteudo do novo prompt",
                "author": "Novo Autor",
                "categories": [str(sample_category.id)],
                "providers": [str(sample_provider.id)],
            },
        )
        assert response.status_code == 302

        prompt = db_session.query(Prompt).filter_by(title="Novo Prompt").first()
        assert prompt is not None
        assert prompt.is_approved is False
        assert prompt.author == "Novo Autor"
        assert len(prompt.categories) == 1
        assert len(prompt.providers) == 1

    def test_post_with_missing_fields(self):
        client = Client()
        response = client.post("/enviar/", {"title": "", "content": "", "author": ""})
        assert response.status_code == 200
        content = response.content.decode()
        assert "obrigatorio" in content
