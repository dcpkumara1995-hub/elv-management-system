from django.urls import path
from . import views


urlpatterns = [
    path(
        "",
        views.daily_work_list,
        name="daily_work_list"
    ),

    path(
        "add/",
        views.daily_work_add,
        name="daily_work_add"
    ),

    path(
        "edit/<int:work_id>/",
        views.daily_work_edit,
        name="daily_work_edit"
    ),

    path(
        "delete/<int:work_id>/",
        views.daily_work_delete,
        name="daily_work_delete"
    ),

    path(
        "report/",
        views.daily_work_report,
        name="daily_work_report"
    ),

    path(
        "report/pdf/",
        views.daily_work_pdf,
        name="daily_work_pdf"
    ),
]