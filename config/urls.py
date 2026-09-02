from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from app.views import dashboard, iit_project


# =========================================================
# HEALTH CHECK
# =========================================================

def health_check(request):

    return JsonResponse(
        {
            "status": "ok"
        }
    )


# =========================================================
# URL PATTERNS
# =========================================================

urlpatterns = [

    # =====================================================
    # DJANGO ADMIN
    # =====================================================

    path(
        "admin/",
        admin.site.urls
    ),

    # =====================================================
    # ACCOUNTS
    # LOGIN / LOGOUT
    # SUPER USER
    # USER MANAGEMENT
    # CHANGE PASSWORD
    # =====================================================

    path(
        "",
        include("accounts.urls")
    ),

    # =====================================================
    # STOCK
    # =====================================================

    path(
        "stock/",
        include("stock.urls")
    ),

    # =====================================================
    # ATTENDANCE
    # =====================================================

    path(
        "attendance/",
        include("attendance.urls")
    ),

    # =====================================================
    # NORMAL DASHBOARD
    # =====================================================

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    # =====================================================
    # IIT PROJECT
    # =====================================================

    path(
        "iit-project/",
        iit_project,
        name="iit_project"
    ),

    # =====================================================
    # HEALTH CHECK
    # =====================================================

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
]
