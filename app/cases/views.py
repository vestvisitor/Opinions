from django.http import HttpResponse
from .models import Case
from django.shortcuts import redirect, render, reverse


def index(request, offset: int | None = 0, limit: int = 5):
    cases = Case.objects.all()[offset:limit]

    if request.user.is_authenticated:
        return render(
            request,
            "cases/cases_page.html",
            context={"authenticated": True, "data": cases}
        )
    else:
        return render(
            request,
            "cases/cases_page.html",
            context={"data": cases}
        )


def study(request, case_id):
    pass


def comment(request, case_id):
    pass


def publish(request):
    pass
