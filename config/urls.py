from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect

from app.views import dashboard, iit_project


def root_redirect(request):

    return redirect("login")


def health_check(request):

    return JsonResponse({"status": "ok"})


urlpatterns = [

    path("", root_redirect, name="root"),

    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),

    path("stock/", include("stock.urls")),

    path("attendance/", include("attendance.urls")),

    path("daily-works/", include("dailyworks.urls")),

    path("dashboard/", dashboard, name="dashboard"),

    path("iit-project/", iit_project, name="iit_project"),

    path("health/", health_check, name="health"),

    path("health", health_check, name="health_no_slash"),

]
