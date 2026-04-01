from django.contrib import admin
from django.urls import include, path

from apps.prompts import admin_views

urlpatterns = [
    path(
        "admin/painel/",
        admin_views.dashboard,
        name="admin_dashboard",
    ),
    path(
        "admin/prompts/",
        admin_views.prompt_list,
        name="admin_prompt_list",
    ),
    path(
        "admin/prompts/<int:pk>/aprovar/",
        admin_views.prompt_approve,
        name="admin_prompt_approve",
    ),
    path(
        "admin/prompts/<int:pk>/rejeitar/",
        admin_views.prompt_reject,
        name="admin_prompt_reject",
    ),
    path(
        "admin/categorias/",
        admin_views.category_list,
        name="admin_category_list",
    ),
    path(
        "admin/categorias/<int:pk>/excluir/",
        admin_views.category_delete,
        name="admin_category_delete",
    ),
    path(
        "admin/provedores/",
        admin_views.provider_list,
        name="admin_provider_list",
    ),
    path(
        "admin/provedores/<int:pk>/excluir/",
        admin_views.provider_delete,
        name="admin_provider_delete",
    ),
    path("admin/", admin.site.urls),
    path("", include("apps.prompts.urls")),
]
