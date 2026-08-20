from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from accounts.views import login_view, logout_view
from app.views import dashboard


# ============================================================
# HEALTH CHECK
# ============================================================

def health_check(request):
    return JsonResponse({"status": "ok"})


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Stock Management
    path("stock/", include("stock.urls")),

    # Authentication
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),

    # SnapDeploy health check
    # IMPORTANT: No trailing slash
    path("health", health_check, name="health"),

    # Root URL
    path("", login_view, name="home"),
]