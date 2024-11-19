from django.urls import path

from . import views

handler404 ='views.not_found_view'

app_name = "cases"
urlpatterns = [
    path("number/<int:case_id>/", views.case, name="case"),
    path("number/opinion/<int:case_id>/", views.opinion, name="opinion"),
    path("delete/<int:case_id>/", views.delete, name="delete"),
    path("edit/<int:case_id>/", views.edit, name="edit"),
    path("publish/", views.publish, name="publish"),
    path("opinions/", views.my_opinions, name="opinions"),
    path("my/", views.my_cases, name="my_cases"),
    path("", views.index, name="index"),
]
