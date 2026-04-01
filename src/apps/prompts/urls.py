from django.urls import path

from . import views

app_name = "prompts"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/prompts/", views.prompt_list_api, name="prompt_list_api"),
    path(
        "api/prompts/<int:prompt_id>/",
        views.prompt_detail_api,
        name="prompt_detail_api",
    ),
    path("enviar/", views.submit, name="submit"),
]
