from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("signout/", views.signout, name="signout"),
    path("me/", views.me, name="me"),
    path("profile/<str:username>/", views.profile, name="profile"),
]
