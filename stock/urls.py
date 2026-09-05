from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.stock_home,
        name="stock_home"
    ),

    path(
        "update/",
        views.stock_update,
        name="stock_update"
    ),

    path(
        "add-item/",
        views.add_item,
        name="add_item"
    ),

    path(
        "delete/<int:item_id>/",
        views.delete_item,
        name="delete_item"
    ),

    path(
        "current/",
        views.current_stock,
        name="current_stock"
    ),

    path(
        "reports/",
        views.reports,
        name="reports"
    ),

]