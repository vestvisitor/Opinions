from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, reverse
from django.contrib import messages

from .forms import UserSigninForm, UserSignupForm


def index(request, offset: int | None = 0, limit: int = 5):

    if request.user.is_authenticated:
        users = User.objects.all().filter(~Q(username=request.user.username))[offset:limit]
        return render(
            request,
            "users/people_page.html",
            context={"authenticated": True, "data": users}
        )
    else:
        users = User.objects.all()[offset:limit]
        return render(
            request,
            "users/people_page.html",
            context={"data": users}
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

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                request.session.set_expiry(300)
                login(request, user)
                return redirect(reverse("index"))
        else:
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

        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password"]
        password2 = request.POST["password_confirm"]

        try:
            User.objects.get(username=username)
            messages.error(request, "account with this username already exists")
            return redirect(reverse("users:signup"))
        except User.DoesNotExist:
            pass

        try:
            User.objects.get(email=email)
            messages.error(request, "account with this email already exists")
            return redirect(reverse("users:signup"))
        except User.DoesNotExist:
            pass

        if password1 != password2:
            messages.error(request, "passwords don't match")
            return redirect(reverse("users:signup"))

        new_user = User.objects.create_user(username, email, password1)
        new_user.save()

        return redirect(reverse("index"))


def signout(request):

    if request.user.is_authenticated:

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

    context = {"user": user}

    if request.user.is_authenticated:
        context["authenticated"] = True
        if request.user.username == username:
            return redirect(reverse("users:me"))

    return render(
        request,
        "users/user_page.html",
        context
    )


def me(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        return render(
            request,
            "users/profile_page.html",
            context={"authenticated": True, "user": user}
        )
    else:
        return redirect(reverse("users:signin"))
