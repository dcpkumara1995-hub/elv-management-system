from django.db import models
from django.contrib.auth.models import User


class DailyWork(models.Model):

    date = models.DateField()

    work = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-date",
            "-created_at"
        ]

    def __str__(self):

        return f"{self.date} - {self.work[:50]}"
