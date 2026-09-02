from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # LOGIN / LOGOUT
    # =====================================================

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # =====================================================
    # SUPER USER DASHBOARD
    # =====================================================

    path(
        "superuser/",
        views.superuser_dashboard,
        name="superuser_dashboard"
    ),

    # =====================================================
    # USER MANAGEMENT
    # =====================================================

    path(
        "superuser/users/",
        views.user_management,
        name="user_management"
    ),

    path(
        "superuser/users/create/",
        views.create_user,
        name="create_user"
    ),

    path(
        "superuser/users/edit/<int:user_id>/",
        views.edit_user,
        name="edit_user"
    ),

    path(
        "superuser/users/password/<int:user_id>/",
        views.reset_user_password,
        name="reset_user_password"
    ),

    path(
        "superuser/users/toggle/<int:user_id>/",
        views.toggle_user,
        name="toggle_user"
    ),

    # =====================================================
    # CHANGE MY PASSWORD
    # =====================================================

    path(
        "change-password/",
        views.change_password,
        name="change_password"
    ),
]
