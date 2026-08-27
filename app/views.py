from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, "app/dashboard.html")


@login_required
def iit_project(request):
    return render(request, "app/iit_project.html")


@login_required
def attendance(request):
    return render(request, "app/attendance.html")