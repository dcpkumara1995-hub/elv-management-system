from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from accounts.views import login_view, logout_view
from app.views import dashboard


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),

    path("stock/", include("stock.urls")),

    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),

    # SnapDeploy health check
    path("health/", health_check, name="health"),

    # Root URL
    path("", login_view, name="home"),
]