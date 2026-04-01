from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render

from db.engine import get_db

from . import services


def index(request):
    with get_db() as session:
        return render(
            request,
            "prompts/index.html",
            {
                "categories": services.list_categories(session),
                "providers": services.list_providers(session),
            },
        )


def prompt_list_api(request):
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 12))
    search = request.GET.get("search", "").strip()
    category_ids_raw = request.GET.get("categories", "")
    provider_ids_raw = request.GET.get("providers", "")

    category_ids = (
        [int(i) for i in category_ids_raw.split(",") if i.strip()]
        if category_ids_raw
        else None
    )
    provider_ids = (
        [int(i) for i in provider_ids_raw.split(",") if i.strip()]
        if provider_ids_raw
        else None
    )

    with get_db() as session:
        data = services.list_approved_prompts(
            session,
            page=page,
            page_size=page_size,
            search=search,
            category_ids=category_ids,
            provider_ids=provider_ids,
        )

    return JsonResponse(data)


def prompt_detail_api(request, prompt_id):
    with get_db() as session:
        data = services.get_prompt_detail(session, prompt_id)

    if data is None:
        return JsonResponse({"error": "Prompt not found"}, status=404)

    return JsonResponse(data)


def submit(request):
    with get_db() as session:
        categories = services.list_categories(session)
        providers = services.list_providers(session)

        if request.method == "POST":
            title = request.POST.get("title", "").strip()
            content = request.POST.get("content", "").strip()
            author = request.POST.get("author", "").strip()
            category_ids = request.POST.getlist("categories")
            provider_ids = request.POST.getlist("providers")

            errors = []
            if not title:
                errors.append("O titulo e obrigatorio.")
            if not content:
                errors.append("O conteudo e obrigatorio.")
            if not author:
                errors.append("O autor e obrigatorio.")

            if errors:
                return render(
                    request,
                    "prompts/submit.html",
                    {
                        "categories": categories,
                        "providers": providers,
                        "errors": errors,
                        "form_data": {
                            "title": title,
                            "content": content,
                            "author": author,
                            "category_ids": category_ids,
                            "provider_ids": provider_ids,
                        },
                    },
                )

            services.create_prompt(
                session,
                title=title,
                content=content,
                author=author,
                category_ids=[int(i) for i in category_ids],
                provider_ids=[int(i) for i in provider_ids],
            )

            messages.success(
                request,
                "Prompt enviado com sucesso! Ele sera exibido apos aprovacao.",
            )
            return redirect("prompts:index")

        return render(
            request,
            "prompts/submit.html",
            {
                "categories": categories,
                "providers": providers,
                "form_data": {},
            },
        )
