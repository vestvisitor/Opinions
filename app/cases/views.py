from dataclasses import dataclass

from django.http import HttpResponse
from django.utils import timezone
from .forms import CaseCreateForm, CaseEditForm, OpinionCreateForm
from .models import Case, Opinion, CaseTag
from django.shortcuts import redirect, render, reverse
from django.db.models import Q


def index(request, offset: int | None = 0, limit: int = 5):

    if request.user.is_authenticated:
        cases = Case.objects.all().filter(~Q(creator=request.user.id))[offset:limit]
        return render(
            request,
            "cases/cases_page.html",
            context={"authenticated": True, "data": cases}
        )
    else:
        cases = Case.objects.all()[offset:limit]
        return render(
            request,
            "cases/cases_page.html",
            context={"data": cases}
        )


def my_cases(request, offset: int | None = 0, limit: int = 5):
    if request.user.is_authenticated:
        cases = Case.objects.all().filter(creator=request.user.id)[offset:limit]
        return render(
            request,
            "cases/cases_page.html",
            context={"authenticated": True, "my": True, "data": cases}
        )
    else:
        return redirect(reverse("users:signin"))


def case(request, case_id: int, offset: int | None = 0, limit: int = 5):

    context = {}

    if request.user.is_authenticated:
        context["authenticated"] = True

    try:
        requested_case = Case.objects.get(id=case_id)
        context["case"] = requested_case
    except Case.DoesNotExist:
        return HttpResponse("Such case does not exist")

    if request.user.pk != requested_case.creator.pk:
        form = OpinionCreateForm(case_id=case_id)
        context["form"] = form

    try:
        opinions = Opinion.objects.all().filter(case_id=requested_case.id)[offset:limit]
        context["opinions"] = opinions
    except Opinion.DoesNotExist:
        pass

    return render(
        request,
        "cases/case_page.html",
        context
    )


def new_case(request):
    if not request.user.is_authenticated:
        return redirect(reverse("users:signin"))
    else:
        context = {"authenticated": True}

    context["form"] = CaseCreateForm()

    return render(
        request,
        "cases/new_case_page.html",
        context
    )


def delete(request, case_id: int):

    if request.user.is_authenticated and request.method == "POST":
        try:
            condition1 = Q(id=case_id)
            condition2 = Q(creator=request.user.id)
            Case.objects.filter(condition1 & condition2).delete()
        except Case.DoesNotExist:
            return HttpResponse("Such case does not exist")

    return redirect(reverse("cases:my_cases"))


def publish(request):

    if not request.user.is_authenticated:
        return redirect(reverse("users:signin"))
    else:
        context = {"authenticated": True}

    if request.method == "GET":
        context["form"] = CaseCreateForm()

        return render(
            request,
            "cases/new_case_page.html",
            context
        )

    elif request.method == 'POST':
        data = CaseCreateForm(request.POST)
        new = data.save(commit=False)

        new.pub_date = timezone.now()
        new.creator = request.user

        new.save()
        data.save_m2m()

        return redirect(reverse("cases:my_cases"))


def edit(request, case_id: int):
    if not request.user.is_authenticated:
        return redirect(reverse("users:signin"))

    try:
        requested_case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return HttpResponse("Such case does not exist")

    if requested_case.creator != request.user:
        return redirect(reverse("cases:index"))

    if request.method == "GET":

        context = {"authenticated": True, "edit": True, "case": requested_case}

        selected_tags = [i['id'] for i in requested_case.tags.values()]

        context['form'] = CaseEditForm(
            initial={
                "case_title": requested_case.case_title,
                "tags": selected_tags,
                "case_text": requested_case.case_text,
                "is_anonymous": requested_case.is_anonymous
            }
        )

        return render(
            request,
            "cases/new_case_page.html",
            context
        )

    elif request.method == 'POST':

        form = CaseEditForm(request.POST, instance=requested_case)
        form.save()

        return redirect(reverse("cases:my_cases"))


def opinion(request, case_id: int):
    if not request.user.is_authenticated:
        return redirect(reverse("users:signin"))

    if request.method == "POST":

        form_data = OpinionCreateForm(request.POST, case_id=case_id)

        user_opinion = form_data.save(commit=False)

        user_opinion.pub_date = timezone.now()
        user_opinion.creator = request.user
        user_opinion.case = Case.objects.get(id=form_data.data['caseid'])

        user_opinion.save()
        form_data.save_m2m()

        return redirect(reverse("cases:case", kwargs={'case_id': form_data.data['caseid']}))
