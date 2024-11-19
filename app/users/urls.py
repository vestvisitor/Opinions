from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("signout/", views.signout, name="signout"),
    path("me/", views.me, name="me"),
    path("me/edit/", views.edit_profile, name="edit"),
    path("me/edit/password/", views.edit_password, name="edit_password"),
    path("profile/<str:username>/", views.profile, name="profile"),
]
