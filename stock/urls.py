from django.urls import path
from . import views

urlpatterns = [
    path("update/", views.stock_update, name="stock_update"),
    path("current/", views.current_stock, name="current_stock"),
    path("reports/", views.reports, name="reports"),
]