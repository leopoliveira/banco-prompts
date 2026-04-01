from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from sqlalchemy import select

from db.engine import get_db

from .models import Category, LLMProvider


@staff_member_required
def category_list(request):
    with get_db() as session:
        if request.method == "POST":
            name = request.POST.get("name", "").strip()
            if name:
                category = Category(name=name)
                session.add(category)
                session.commit()
            return redirect("admin_category_list")

        categories = session.scalars(select(Category).order_by(Category.name)).all()
        return render(
            request,
            "admin/sqla_list.html",
            {
                "title": "Categorias",
                "items": categories,
                "add_label": "Nova Categoria",
                "delete_url_name": "admin_category_delete",
            },
        )


@staff_member_required
def category_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    with get_db() as session:
        category = session.get(Category, pk)
        if category:
            session.delete(category)
            session.commit()
    return redirect("admin_category_list")


@staff_member_required
def provider_list(request):
    with get_db() as session:
        if request.method == "POST":
            name = request.POST.get("name", "").strip()
            if name:
                provider = LLMProvider(name=name)
                session.add(provider)
                session.commit()
            return redirect("admin_provider_list")

        providers = session.scalars(
            select(LLMProvider).order_by(LLMProvider.name)
        ).all()
        return render(
            request,
            "admin/sqla_list.html",
            {
                "title": "Provedores LLM",
                "items": providers,
                "add_label": "Novo Provedor",
                "delete_url_name": "admin_provider_delete",
            },
        )


@staff_member_required
def provider_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    with get_db() as session:
        provider = session.get(LLMProvider, pk)
        if provider:
            session.delete(provider)
            session.commit()
    return redirect("admin_provider_list")
