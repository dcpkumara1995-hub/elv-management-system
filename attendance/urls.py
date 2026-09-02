from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # ATTENDANCE HOME
    # =====================================================

    path(
        '',
        views.attendance_home,
        name='attendance_home'
    ),

    # =====================================================
    # CHAMARA ATTENDANCE
    # =====================================================

    path(
        'employee/',
        views.employee_attendance,
        name='employee_attendance'
    ),

    # =====================================================
    # NIMALKA ATTENDANCE
    # =====================================================

    path(
        'nimalka/',
        views.nimalka_attendance,
        name='nimalka_attendance'
    ),

    # =====================================================
    # LABOUR ATTENDANCE
    # =====================================================

    path(
        'labour/',
        views.labour_attendance,
        name='labour_attendance'
    ),

    # =====================================================
    # LABOUR MANAGEMENT
    # SUPER ADMIN ONLY
    # =====================================================

    path(
        'labour-management/',
        views.labour_management,
        name='labour_management'
    ),

    path(
        'labour-management/add/',
        views.labour_add,
        name='labour_add'
    ),

    path(
        'labour-management/edit/<int:employee_id>/',
        views.labour_edit,
        name='labour_edit'
    ),

    path(
        'labour-management/toggle/<int:employee_id>/',
        views.labour_toggle,
        name='labour_toggle'
    ),

    # =====================================================
    # ATTENDANCE HISTORY
    # =====================================================

    path(
        'history/',
        views.attendance_history,
        name='attendance_history'
    ),

    # =====================================================
    # ATTENDANCE PDF
    # =====================================================

    path(
        'history/pdf/',
        views.attendance_pdf,
        name='attendance_pdf'
    ),
]