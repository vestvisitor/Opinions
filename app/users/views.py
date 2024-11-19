from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.contrib import messages
from .forms import UserSigninForm, UserSignupForm, UserEditForm, UserChangePasswordForm
from cases.models import Case, Opinion
from django.contrib.auth.decorators import login_required


def index(request, offset: int | None = 0, limit: int = 5):

    if request.user.is_authenticated:
        context = {"authenticated": True}
        users = User.objects.exclude(username=request.user.username).all()[offset:limit]
    else:
        context = {"authenticated": False}
        users = User.objects.all()[offset:limit]

    for user in users:
        user.cases_number = Case.objects.filter(creator=user.id).count()
        user.opinions_number = Opinion.objects.filter(creator=user.id).count()

    context["data"] = users

    return render(
        request,
        "users/people_page.html",
        context
    )


def signin(request):

    if request.user.is_authenticated:
        return redirect(reverse("users:me"))

    if request.method == "GET":

        return render(
            request,
            "users/signin_page.html",
            {"form": UserSigninForm()}
            )

    elif request.method == "POST":

        form = UserSigninForm(request.POST)

        if not form.is_valid():
            user = authenticate(request, username=form.data['username'], password=form.data['password'])
            if user is not None:
                if user.is_active:
                    request.session.set_expiry(300*30)
                    login(request, user)
                    return redirect(reverse("index"))

        messages.error(request, 'incorrect credentials')
        return redirect(reverse("users:signin"))


def signup(request):

    if request.user.is_authenticated:
        return redirect(reverse("users:me"))

    if request.method == "GET":

        return render(
            request,
            "users/signup_page.html",
            {"form": UserSignupForm()}
        )

    elif request.method == "POST":

        form = UserSignupForm(request.POST)

        if form.is_valid() and form.validate_email():

            data = form.clean()

            new_user = User.objects.create_user(
                data["username"],
                data["email"],
                data["password1"]
            )
            new_user.save()

            return redirect(reverse("index"))

        return render(
            request,
            "users/signup_page.html",
            {"form": form}
        )


@login_required(login_url="/users/signin")
def signout(request):
    if request.method == "POST":
        logout(request)
        return redirect(reverse("index"))
    else:
        return redirect(reverse("users:signin"))


def profile(request, username: str):

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return redirect(reverse("index"))

    context = {
        "user": user,
        "cases": Case.objects.filter(creator=user.id).count(),
        "opinions": Opinion.objects.filter(creator=user.id).count()
    }

    if request.user.is_authenticated:
        context["authenticated"] = True
        if request.user.username == username:
            return redirect(reverse("users:me"))

    return render(
        request,
        "users/user_page.html",
        context
    )


@login_required(login_url="/users/signin")
def me(request):
    user = User.objects.get(username=request.user.username)

    context = {
        "authenticated": True,
        "user": User.objects.get(username=request.user.username),
        "cases": Case.objects.filter(creator=user.id).count(),
        "opinions": Opinion.objects.filter(creator=user.id).count()
    }

    return render(
        request,
        "users/profile_page.html",
        context
    )


@login_required(login_url="/users/signin")
def edit_profile(request):

    context = {"authenticated": True}

    if request.method == "GET":
        context["form"] = UserEditForm(
            initial={
                "username": request.user.username,
                "email": request.user.email,
            }
        )
        return render(
            request,
            "users/edit_profile_page.html",
            context
        )
    elif request.method == "POST":

        form = UserEditForm(request.POST, instance=request.user)

        new_username = form.data.get('username')
        if new_username != request.user.username:
            try:
                user = form.save(commit=False)
                user.username = new_username
            except ValueError:
                pass

        new_email = form.data.get('email')
        if new_email != form.initial.get('email'):
            try:
                 if form.validate_email():
                    user.email = new_email
            except ValueError:
                pass

        if not form.errors:
            form.save()
            return redirect(reverse("users:edit"))
        else:
            context['form'] =form
            return render(
                request,
                "users/edit_profile_page.html",
                context
            )


@login_required(login_url="/users/signin")
def edit_password(request):

    context = {"authenticated": True}

    if request.method == "GET":
        context["form"] = UserChangePasswordForm(request.user)
        return render(
            request,
            "users/edit_profile_page.html",
            context
        )
    elif request.method == "POST":

        form = UserChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)

        context['form'] = form
        return render(
            request,
            "users/edit_profile_page.html",
            context
        )
