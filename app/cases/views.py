from django.http import HttpResponse
from django.utils import timezone
from .forms import CaseCreateForm, CaseEditForm, OpinionCreateForm
from .models import Case, Opinion, CaseTag, CaseOpinion
from django.shortcuts import redirect, render, reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required


def index(request, offset: int | None = 0, limit: int = 5):

    if request.user.is_authenticated:
        cases = Case.objects.filter(~Q(creator=request.user.id)).all()[offset:limit]
        context = {
            "authenticated": True,
            "data": cases
        }
    else:
        cases = Case.objects.all()[offset:limit]
        context = {
            "data": cases
        }

    for c in cases:
        c.commentators = CaseOpinion.objects.filter(case=c).all()
        for k in c.commentators:
            print(k.opinion.creator.username)

    return render(
        request,
        "cases/cases_page.html",
        context
    )


@login_required(login_url="/users/signin/")
def my_cases(request, offset: int | None = 0, limit: int = 5):

    cases = Case.objects.filter(creator=request.user.id).all()[offset:limit]
    return render(
        request,
        "cases/cases_page.html",
        context={"authenticated": True, "my": True, "data": cases}
    )


def case(request, case_id: int, offset: int | None = 0, limit: int = 5):

    context = {}

    if request.user.is_authenticated:
        context["authenticated"] = True

    try:
        requested_case = Case.objects.get(id=case_id)
        context["case"] = requested_case
    except Case.DoesNotExist:
        return redirect(reverse("cases/index"))

    if request.user.pk != requested_case.creator.pk:
        context["form"] = OpinionCreateForm(case_id=case_id)

    try:
        condition1 = Q(case=requested_case)
        condition2 = Q(opinion__creator__id=request.user.id)
        CaseOpinion.objects.get(condition1 & condition2)
        context["restrict"] = True
    except CaseOpinion.DoesNotExist:
        pass

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
        try:
            condition1 = Q(id=case_id)
            condition2 = Q(creator=request.user.id)
            Case.objects.filter(condition1 & condition2).delete()
        except Case.DoesNotExist:
            return redirect(reverse("cases:my_cases"))

    return redirect(reverse("cases:my_cases"))


@login_required(login_url="/users/signin/")
def publish(request):

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

        if data.is_valid():
            new = data.save(commit=False)

            new.pub_date = timezone.now()
            new.creator = request.user

            new.save()
            data.save_m2m()

            return redirect(reverse("cases:my_cases"))


@login_required(login_url="/users/signin/")
def edit(request, case_id: int):

    try:
        requested_case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return redirect(reverse("cases:my_cases"))

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

        if form.is_valid():
            form.save()

        return redirect(reverse("cases:my_cases"))


@login_required(login_url="/users/signin/")
def opinion(request, case_id: int):

    if request.method == "POST":

        form_data = OpinionCreateForm(request.POST, case_id=case_id)

        if form_data.is_valid():

            user_opinion = form_data.save(commit=False)

            requested_case = Case.objects.get(id=form_data.data['caseid'])

            try:
                condition1 = Q(case=requested_case)
                condition2 = Q(opinion__creator__id=request.user.id)
                CaseOpinion.objects.get(condition1 & condition2)
            except CaseOpinion.DoesNotExist:
                pass
            else:
                return redirect(reverse("cases:case", kwargs={'case_id': form_data.data['caseid']}))

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


@login_required(login_url="/users/signin/")
def my_opinions(request, offset: int | None = 0, limit: int = 5):
    context = {"authenticated": True}

    data = CaseOpinion.objects.filter(opinion__creator__id=request.user.id).all()[offset:limit]

    if data:
        context["data"] = data

    return render(
        request,
        "cases/opinions_page.html",
        context
    )
