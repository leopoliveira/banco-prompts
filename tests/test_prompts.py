from django.test import RequestFactory

from apps.prompts.views import index


def test_index_returns_ok():
    factory = RequestFactory()
    request = factory.get("/")
    response = index(request)
    assert response.status_code == 200
