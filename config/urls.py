from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view, logout_view
from app.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("stock/", include("stock.urls")),

    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
]