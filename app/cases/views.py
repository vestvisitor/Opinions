from lib2to3.fixes.fix_input import context

from django.utils import timezone
from .forms import CaseCreateForm, CaseEditForm, OpinionCreateForm
from .models import Case, Opinion, CaseTag, CaseOpinion
from django.shortcuts import redirect, render, reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import random


def index(request):

    context = {}

    if request.user.is_authenticated:
        cases = Case.objects.exclude(creator=request.user.id).order_by('id')
        context["authenticated"] = True
    else:
        cases = Case.objects.get_queryset().order_by('id')

    for c in cases:
        c.commentators = CaseOpinion.objects.filter(case=c).all()

    paginator = Paginator(cases, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context["page_obj"] = page_obj
    context["cases"] = len(cases)

    return render(
        request,
        "cases/cases_page.html",
        context
    )


@login_required(login_url="/users/signin/")
def my_cases(request):
    cases = Case.objects.filter(creator=request.user.id).order_by('id')
    paginator = Paginator(cases, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "cases/cases_page.html",
        context={"authenticated": True, "my": True, "page_obj": page_obj, "cases": len(cases)}
    )


def case(request, case_id: int, offset: int | None = 0, limit: int = 5):

    context = {}

    if request.user.is_authenticated:
        context["authenticated"] = True

    try:
        requested_case = Case.objects.get(id=case_id)
        context["case"] = requested_case
    except Case.DoesNotExist:
        return redirect(reverse("cases:index"))

    if request.user.pk != requested_case.creator.pk:
        try:
            condition1 = Q(case=requested_case)
            condition2 = Q(opinion__creator__id=request.user.id)
            CaseOpinion.objects.get(condition1 & condition2)
        except CaseOpinion.DoesNotExist:
            context["form"] = OpinionCreateForm(case_id=case_id)
    else:
        context['same'] = True

    try:
        opinions = Opinion.objects.filter(case_id=requested_case.id).all()[offset:limit]
        context["opinions"] = opinions
    except Opinion.DoesNotExist:
        pass

    return render(
        request,
        "cases/case_page.html",
        context
    )


@login_required(login_url="/users/signin/")
def delete(request, case_id: int):

    if request.method == "POST":
        requested_case = Case.objects.filter(id=case_id).first()
        if not requested_case:
            return render(request, "cases/cases_page.html", status=404)

        if requested_case.creator != request.user:
            return render(request, "cases/cases_page.html", status=403)

        Case.objects.filter(id=case_id).delete()

        return redirect(reverse("cases:my_cases"))


@login_required(login_url="/users/signin/")
def publish(request):

    context = {"authenticated": True, "form": CaseCreateForm()}

    if request.method == "GET":

        return render(
            request,
            "cases/new_case_page.html",
            context
        )

    elif request.method == 'POST':

        data = CaseCreateForm(request.POST)

        if data.is_valid():
            new = data.save(commit=False)

            new.pub_date = timezone.now()
            new.creator = request.user

            new.save()
            data.save_m2m()

            return redirect(reverse("cases:my_cases"))

        return render(
            request,
            "cases/new_case_page.html",
            context,
            status=422
        )


@login_required(login_url="/users/signin/")
def edit(request, case_id: int):

    try:
        requested_case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return redirect(reverse("cases:my_cases"))

    if requested_case.creator != request.user:
        return redirect(reverse("cases:index"))

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

    if request.method == "GET":

        return render(
            request,
            "cases/new_case_page.html",
            context
        )

    elif request.method == 'POST':

        form = CaseEditForm(request.POST, instance=requested_case)

        if form.is_valid():
            form.save()
            return redirect(reverse("cases:my_cases"))

        return render(
            request,
            "cases/new_case_page.html",
            context,
            status=422
        )


@login_required(login_url="/users/signin/")
def opinion(request, case_id: int):

    if request.method == "POST":

        try:
            requested_case = Case.objects.get(id=request.POST['caseid'])

        except Case.DoesNotExist:
            return render(
                request,
                "cases/cases_page.html",
                {"authenticated": True},
                status=404
            )

        condition1 = Q(case=requested_case)
        condition2 = Q(opinion__creator=request.user)
        if not CaseOpinion.objects.filter(condition1 & condition2).first():
            form_data = OpinionCreateForm(request.POST, case_id=request.POST['caseid'])

            if form_data.is_valid():
                user_opinion = form_data.save(commit=False)

                user_opinion.creator = request.user
                user_opinion.case = requested_case
                user_opinion.pub_date = timezone.now()

                user_opinion.save()
                form_data.save_m2m()

                # create relation between one opinion and one case
                data = CaseOpinion(
                    case=requested_case,
                    opinion=user_opinion
                )

                data.save()

                return redirect(reverse("cases:case", kwargs={'case_id': form_data.data['caseid']}))

        return render(
            request,
            "cases/cases_page.html",
            {"authenticated": True},
            status=422
        )


@login_required(login_url="/users/signin/")
def my_opinions(request):

    opinions = CaseOpinion.objects.filter(opinion__creator__id=request.user.id).order_by('id')

    paginator = Paginator(opinions, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "cases/opinions_page.html",
        {"authenticated": True, "page_obj": page_obj, "opinions": len(opinions)}
    )
