from django.db import models
from django.contrib.auth.models import User


class UserAccess(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="access"
    )

    dashboard = models.BooleanField(
        default=False
    )

    iit_project = models.BooleanField(
        default=False
    )

    stock_update = models.BooleanField(
        default=False
    )

    current_stock = models.BooleanField(
        default=False
    )

    stock_report = models.BooleanField(
        default=False
    )

    attendance = models.BooleanField(
        default=False
    )

    daily_works = models.BooleanField(
        default=False
    )

    user_management = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} Access"