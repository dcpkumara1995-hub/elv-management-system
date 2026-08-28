from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from accounts.views import login_view, logout_view
from app.views import dashboard, iit_project


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "stock/",
        include("stock.urls")
    ),

    path(
        "attendance/",
        include("attendance.urls")
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    path(
        "iit-project/",
        iit_project,
        name="iit_project"
    ),

    path(
        "health/",
        health_check,
        name="health"
    ),

    path(
        "health",
        health_check,
        name="health_no_slash"
    ),

    path(
        "",
        login_view,
        name="home"
    ),
]