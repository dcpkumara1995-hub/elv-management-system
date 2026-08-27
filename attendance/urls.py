from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.attendance_home,
        name='attendance_home'
    ),

    path(
        'employee/',
        views.employee_attendance,
        name='employee_attendance'
    ),

    path(
        'nimalka/',
        views.nimalka_attendance,
        name='nimalka_attendance'
    ),

    path(
        'labour/',
        views.labour_attendance,
        name='labour_attendance'
    ),

    path(
        'history/',
        views.attendance_history,
        name='attendance_history'
    ),

    path(
        'history/pdf/',
        views.attendance_pdf,
        name='attendance_pdf'
    ),
]