from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):

    ROLE_CHOICES = [
        ("EMPLOYEE", "Employee"),
        ("SUPERVISOR", "Supervisor"),
        ("LABOUR", "Labour"),
    ]

    name = models.CharField(max_length=200)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"


class Attendance(models.Model):

    STATUS_CHOICES = [
        ("WORKED", "Worked"),
        ("NOT_WORKED", "Not Worked"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()

    project = models.CharField(
        max_length=200,
        default="IIT Project"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    note = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_created"
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_updated"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-date", "employee__name"]

        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date", "project"],
                name="unique_employee_date_project"
            )
        ]

    def __str__(self):
        return (
            f"{self.employee.name} - "
            f"{self.date} - "
            f"{self.status}"
        )