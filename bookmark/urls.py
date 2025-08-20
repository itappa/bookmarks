from django.urls import path

from . import views
from .views import ItemListView

app_name = "bookmark"

urlpatterns = [
    path("edit/<int:pk>/", views.edit_view, name="edit"),
    path("delete/<int:pk>/", views.delete_view, name="delete"),
    path("add/", views.add_bookmark, name="add_bookmark"),
    path("quick-add/", views.quick_add_bookmark, name="quick_add_bookmark"),
    path("fetch-ogp/", views.fetch_ogp_data, name="fetch_ogp_data"),
    path("category/<str:str>/", views.item_list_by_category, name="item_list_by_category"),
    path("table/", views.table, name="table"),
    path("list/", views.list, name="list"),
    path("", ItemListView.as_view(), name="index"),
]
