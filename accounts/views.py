from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import UserAccess


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:

        if request.user.is_superuser:
            return redirect("superuser_dashboard")

        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if not user.is_active:

                return render(
                    request,
                    "accounts/login.html",
                    {
                        "error": (
                            "Your account is inactive. "
                            "Please contact the administrator."
                        )
                    }
                )

            login(request, user)

            # Super User → Super User Dashboard
            if user.is_superuser:
                return redirect("superuser_dashboard")

            # Normal User → Normal Dashboard
            return redirect("dashboard")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password"
            }
        )

    return render(
        request,
        "accounts/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required
def logout_view(request):

    logout(request)

    return redirect("login")


# =========================================================
# SUPER USER DASHBOARD
# SUPER USER ONLY
# =========================================================

@login_required
def superuser_dashboard(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    users = User.objects.all().order_by("username")

    return render(
        request,
        "accounts/superuser_dashboard.html",
        {
            "users": users,
        }
    )


# =========================================================
# USER MANAGEMENT
# SUPER USER ONLY
# =========================================================

@login_required
def user_management(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    users = User.objects.all().order_by("username")

    # Make sure every normal user has an access record
    for user in users:

        if not user.is_superuser:

            UserAccess.objects.get_or_create(
                user=user
            )

    return render(
        request,
        "accounts/user_management.html",
        {
            "users": users,
        }
    )


# =========================================================
# CREATE USER
# SUPER USER ONLY
# =========================================================

@login_required
def create_user(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # PERMISSIONS
        # -------------------------------------------------

        dashboard_access = (
            "dashboard" in request.POST
        )

        iit_project_access = (
            "iit_project" in request.POST
        )

        stock_update_access = (
            "stock_update" in request.POST
        )

        current_stock_access = (
            "current_stock" in request.POST
        )

        stock_report_access = (
            "stock_report" in request.POST
        )

        attendance_access = (
            "attendance" in request.POST
        )

        daily_works_access = (
            "daily_works" in request.POST
        )

        user_management_access = (
            "user_management" in request.POST
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not username:

            messages.error(
                request,
                "Username is required."
            )

            return redirect("create_user")

        if not password:

            messages.error(
                request,
                "Password is required."
            )

            return redirect("create_user")

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("create_user")

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("create_user")

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.is_active = True
        user.is_staff = False
        user.is_superuser = False

        user.save()

        # -------------------------------------------------
        # CREATE USER ACCESS
        # -------------------------------------------------

        UserAccess.objects.create(

            user=user,

            dashboard=dashboard_access,

            iit_project=iit_project_access,

            stock_update=stock_update_access,

            current_stock=current_stock_access,

            stock_report=stock_report_access,

            attendance=attendance_access,

            daily_works=daily_works_access,

            user_management=user_management_access,
        )

        messages.success(
            request,
            f"User '{username}' created successfully."
        )

        return redirect("user_management")

    return render(
        request,
        "accounts/create_user.html"
    )


# =========================================================
# EDIT USER
# SUPER USER ONLY
# =========================================================

@login_required
def edit_user(request, user_id):

    if not request.user.is_superuser:
        return redirect("dashboard")

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        messages.error(
            request,
            "User not found."
        )

        return redirect("user_management")

    # -----------------------------------------------------
    # Super User Access
    # -----------------------------------------------------

    if user.is_superuser:

        access = None

    else:

        access, created = UserAccess.objects.get_or_create(
            user=user
        )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        user.first_name = first_name
        user.last_name = last_name

        user.save()

        # -------------------------------------------------
        # UPDATE PERMISSIONS
        # -------------------------------------------------

        if not user.is_superuser:

            access.dashboard = (
                "dashboard" in request.POST
            )

            access.iit_project = (
                "iit_project" in request.POST
            )

            access.stock_update = (
                "stock_update" in request.POST
            )

            access.current_stock = (
                "current_stock" in request.POST
            )

            access.stock_report = (
                "stock_report" in request.POST
            )

            access.attendance = (
                "attendance" in request.POST
            )

            access.daily_works = (
                "daily_works" in request.POST
            )

            access.user_management = (
                "user_management" in request.POST
            )

            access.save()

        messages.success(
            request,
            f"User '{user.username}' updated successfully."
        )

        return redirect("user_management")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    return render(
        request,
        "accounts/edit_user.html",
        {
            "edit_user": user,
            "access": access,
        }
    )


# =========================================================
# RESET USER PASSWORD
# SUPER USER ONLY
# =========================================================

@login_required
def reset_user_password(request, user_id):

    if not request.user.is_superuser:
        return redirect("dashboard")

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        messages.error(
            request,
            "User not found."
        )

        return redirect("user_management")

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not password:

            messages.error(
                request,
                "Password is required."
            )

            return redirect(
                "reset_user_password",
                user_id=user.id
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "reset_user_password",
                user_id=user.id
            )

        user.set_password(password)

        user.save()

        messages.success(
            request,
            f"Password for '{user.username}' changed successfully."
        )

        return redirect("user_management")

    return render(
        request,
        "accounts/reset_user_password.html",
        {
            "edit_user": user,
        }
    )


# =========================================================
# ACTIVATE / DEACTIVATE USER
# SUPER USER ONLY
# =========================================================

@login_required
def toggle_user(request, user_id):

    if not request.user.is_superuser:
        return redirect("dashboard")

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        messages.error(
            request,
            "User not found."
        )

        return redirect("user_management")

    # -----------------------------------------------------
    # Prevent disabling own account
    # -----------------------------------------------------

    if user.id == request.user.id:

        messages.error(
            request,
            "You cannot deactivate your own account."
        )

        return redirect("user_management")

    user.is_active = not user.is_active

    user.save()

    if user.is_active:

        messages.success(
            request,
            f"User '{user.username}' activated."
        )

    else:

        messages.success(
            request,
            f"User '{user.username}' deactivated."
        )

    return redirect("user_management")


# =========================================================
# CHANGE MY PASSWORD
# NORMAL USERS + SUPER USERS
# =========================================================

@login_required
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get(
            "current_password",
            ""
        )

        new_password = request.POST.get(
            "new_password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not request.user.check_password(
            current_password
        ):

            messages.error(
                request,
                "Current password is incorrect."
            )

            return redirect("change_password")

        if not new_password:

            messages.error(
                request,
                "New password is required."
            )

            return redirect("change_password")

        if new_password != confirm_password:

            messages.error(
                request,
                "New passwords do not match."
            )

            return redirect("change_password")

        request.user.set_password(
            new_password
        )

        request.user.save()

        # Keep the user logged in
        login(
            request,
            request.user
        )

        messages.success(
            request,
            "Your password has been changed successfully."
        )

        if request.user.is_superuser:

            return redirect(
                "superuser_dashboard"
            )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "accounts/change_password.html"
    )