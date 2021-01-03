from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("add_entry", views.add, name="add"),
    path("edit_entry", views.edit, name="edit"),
    path("search", views.search, name="search")
]
