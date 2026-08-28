from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from accounts.views import login_view, logout_view
from app.views import dashboard, iit_project


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [

    # Admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Stock System
    path(
        "stock/",
        include("stock.urls")
    ),

    # Attendance System
    path(
        "attendance/",
        include("attendance.urls")
    ),

    # Login / Logout
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

    # Dashboard
    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    # IIT Project
    path(
        "iit-project/",
        iit_project,
        name="iit_project"
    ),

    # Health Check
    path(
        "health/",
        health_check,
        name="health"
    ),

    # Home
    path(
        "",
        login_view,
        name="home"
    ),
]