from django.urls import path

from . import views

app_name = "rssreader"

urlpatterns = [
    path("", views.index, name="index"),
]

