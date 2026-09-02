from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Attendance, Employee


# =========================================================
# ATTENDANCE HOME
# =========================================================

@login_required
def attendance_home(request):

    return render(
        request,
        "attendance/attendance_home.html"
    )


# =========================================================
# CHAMARA ATTENDANCE
# =========================================================

@login_required
def employee_attendance(request):

    employee = Employee.objects.filter(
        name__icontains="Chamara",
        active=True
    ).first()

    if not employee:
        messages.error(
            request,
            "Chamara employee record not found."
        )

        return redirect("attendance_home")

    if request.method == "POST":

        attendance_date = request.POST.get(
            "attendance_date"
        )

        project = request.POST.get(
            "project",
            ""
        ).strip()

        worked = request.POST.get(
            "worked"
        )

        if not attendance_date:

            messages.error(
                request,
                "Please select a date."
            )

            return redirect(
                "employee_attendance"
            )

        if worked not in [
            "Present",
            "Absent",
            "Half Day"
        ]:

            messages.error(
                request,
                "Please select attendance."
            )

            return redirect(
                "employee_attendance"
            )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        if worked == "Present":

            status = "WORKED"

        elif worked == "Half Day":

            status = "HALF_DAY"

        else:

            status = "NOT_WORKED"

            project = ""

        # -------------------------------------------------
        # PROJECT REQUIRED
        # -------------------------------------------------

        if status in [
            "WORKED",
            "HALF_DAY"
        ] and not project:

            messages.error(
                request,
                "Please select a project."
            )

            return redirect(
                "employee_attendance"
            )

        # -------------------------------------------------
        # SAVE / UPDATE
        # -------------------------------------------------

        attendance, created = (
            Attendance.objects.update_or_create(
                employee=employee,
                date=attendance_date,
                defaults={
                    "project": project,
                    "status": status,
                    "updated_by": request.user,
                }
            )
        )

        if created:

            attendance.created_by = request.user
            attendance.save(
                update_fields=["created_by"]
            )

        messages.success(
            request,
            "Chamara attendance saved successfully."
        )

        return redirect(
            "attendance_history"
        )

    return render(
        request,
        "attendance/employee_attendance.html",
        {
            "employee": employee,
            "today": timezone.localdate(),
        }
    )


# =========================================================
# NIMALKA ATTENDANCE
# =========================================================

@login_required
def nimalka_attendance(request):

    employee = Employee.objects.filter(
        name__icontains="Nimalka",
        active=True
    ).first()

    if not employee:

        messages.error(
            request,
            "Nimalka employee record not found."
        )

        return redirect(
            "attendance_home"
        )

    if request.method == "POST":

        attendance_date = request.POST.get(
            "attendance_date"
        )

        worked = request.POST.get(
            "worked"
        )

        if not attendance_date:

            messages.error(
                request,
                "Please select a date."
            )

            return redirect(
                "nimalka_attendance"
            )

        if worked not in [
            "Present",
            "Absent",
            "Half Day"
        ]:

            messages.error(
                request,
                "Please select attendance."
            )

            return redirect(
                "nimalka_attendance"
            )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        if worked == "Present":

            status = "WORKED"
            project = "IIT Project"

        elif worked == "Half Day":

            status = "HALF_DAY"
            project = "IIT Project"

        else:

            status = "NOT_WORKED"
            project = ""

        # -------------------------------------------------
        # SAVE / UPDATE
        # -------------------------------------------------

        attendance, created = (
            Attendance.objects.update_or_create(
                employee=employee,
                date=attendance_date,
                defaults={
                    "project": project,
                    "status": status,
                    "updated_by": request.user,
                }
            )
        )

        if created:

            attendance.created_by = request.user

            attendance.save(
                update_fields=["created_by"]
            )

        messages.success(
            request,
            "Nimalka attendance saved successfully."
        )

        return redirect(
            "attendance_history"
        )

    return render(
        request,
        "attendance/nimalka_attendance.html",
        {
            "employee": employee,
            "today": timezone.localdate(),
        }
    )


# =========================================================
# LABOUR ATTENDANCE
# =========================================================

@login_required
def labour_attendance(request):

    labour_list = Employee.objects.filter(
        role="LABOUR",
        active=True
    ).order_by("name")

    if request.method == "POST":

        attendance_date = request.POST.get(
            "attendance_date"
        )

        if not attendance_date:

            messages.error(
                request,
                "Please select a date."
            )

            return redirect(
                "labour_attendance"
            )

        if not labour_list.exists():

            messages.error(
                request,
                "No active labour employees found."
            )

            return redirect(
                "labour_attendance"
            )

        saved_count = 0

        for labour in labour_list:

            field_name = f"labour_{labour.id}"

            worked = request.POST.get(
                field_name
            )

            if worked not in [
                "Present",
                "Absent"
            ]:

                continue

            if worked == "Present":

                status = "WORKED"

            else:

                status = "NOT_WORKED"

            attendance, created = (
                Attendance.objects.update_or_create(
                    employee=labour,
                    date=attendance_date,
                    project="IIT Project",
                    defaults={
                        "status": status,
                        "updated_by": request.user,
                    }
                )
            )

            if created:

                attendance.created_by = request.user

                attendance.save(
                    update_fields=["created_by"]
                )

            saved_count += 1

        if saved_count == 0:

            messages.error(
                request,
                "Please select attendance for at least one labour."
            )

        else:

            messages.success(
                request,
                f"{saved_count} labour attendance record(s) saved successfully."
            )

        return redirect(
            "attendance_history"
        )

    return render(
        request,
        "attendance/labour_attendance.html",
        {
            "labour_list": labour_list,
            "today": timezone.localdate(),
        }
    )


# =========================================================
# LABOUR MANAGEMENT
# SUPER ADMIN ONLY
# =========================================================

@login_required
def labour_management(request):

    if not request.user.is_superuser:

        raise PermissionDenied

    labour_list = Employee.objects.filter(
        role="LABOUR"
    ).order_by(
        "-active",
        "name"
    )

    return render(
        request,
        "attendance/labour_management.html",
        {
            "labour_list": labour_list,
        }
    )


# =========================================================
# ADD LABOUR
# SUPER ADMIN ONLY
# =========================================================

@login_required
def labour_add(request):

    if not request.user.is_superuser:

        raise PermissionDenied

    if request.method != "POST":

        return redirect(
            "labour_management"
        )

    name = request.POST.get(
        "name",
        ""
    ).strip()

    if not name:

        messages.error(
            request,
            "Please enter a labour name."
        )

        return redirect(
            "labour_management"
        )

    existing = Employee.objects.filter(
        name__iexact=name,
        role="LABOUR"
    ).first()

    if existing:

        if existing.active:

            messages.error(
                request,
                "This labour already exists."
            )

        else:

            existing.active = True
            existing.save(
                update_fields=["active"]
            )

            messages.success(
                request,
                f"{existing.name} has been activated again."
            )

        return redirect(
            "labour_management"
        )

    Employee.objects.create(
        name=name,
        role="LABOUR",
        active=True
    )

    messages.success(
        request,
        f"{name} added successfully."
    )

    return redirect(
        "labour_management"
    )


# =========================================================
# EDIT LABOUR
# SUPER ADMIN ONLY
# =========================================================

@login_required
def labour_edit(request, employee_id):

    if not request.user.is_superuser:

        raise PermissionDenied

    labour = get_object_or_404(
        Employee,
        id=employee_id,
        role="LABOUR"
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        if not name:

            messages.error(
                request,
                "Labour name cannot be empty."
            )

            return redirect(
                "labour_management"
            )

        duplicate = Employee.objects.filter(
            name__iexact=name,
            role="LABOUR"
        ).exclude(
            id=labour.id
        ).exists()

        if duplicate:

            messages.error(
                request,
                "Another labour with this name already exists."
            )

            return redirect(
                "labour_management"
            )

        labour.name = name

        labour.save(
            update_fields=["name"]
        )

        messages.success(
            request,
            "Labour name updated successfully."
        )

        return redirect(
            "labour_management"
        )

    return render(
        request,
        "attendance/labour_edit.html",
        {
            "labour": labour,
        }
    )


# =========================================================
# ACTIVATE / DEACTIVATE LABOUR
# SUPER ADMIN ONLY
# =========================================================

@login_required
def labour_toggle(request, employee_id):

    if not request.user.is_superuser:

        raise PermissionDenied

    labour = get_object_or_404(
        Employee,
        id=employee_id,
        role="LABOUR"
    )

    if request.method != "POST":

        return redirect(
            "labour_management"
        )

    labour.active = not labour.active

    labour.save(
        update_fields=["active"]
    )

    if labour.active:

        messages.success(
            request,
            f"{labour.name} activated successfully."
        )

    else:

        messages.success(
            request,
            f"{labour.name} deactivated successfully."
        )

    return redirect(
        "labour_management"
    )


# =========================================================
# ATTENDANCE HISTORY
# =========================================================

@login_required
def attendance_history(request):

    records = Attendance.objects.select_related(
        "employee",
        "created_by",
        "updated_by"
    ).all()

    from_date = request.GET.get(
        "from_date"
    )

    to_date = request.GET.get(
        "to_date"
    )

    employee_id = request.GET.get(
        "employee"
    )

    status = request.GET.get(
        "status"
    )

    if from_date:

        records = records.filter(
            date__gte=from_date
        )

    if to_date:

        records = records.filter(
            date__lte=to_date
        )

    if employee_id:

        records = records.filter(
            employee_id=employee_id
        )

    if status:

        records = records.filter(
            status=status
        )

    records = records.order_by(
        "-date",
        "employee__name"
    )

    employees = Employee.objects.filter(
        active=True
    ).order_by(
        "name"
    )

    return render(
        request,
        "attendance/attendance_history.html",
        {
            "records": records,
            "employees": employees,
            "from_date": from_date,
            "to_date": to_date,
            "selected_employee": employee_id,
            "selected_status": status,
        }
    )


# =========================================================
# ATTENDANCE PDF
# =========================================================

@login_required
def attendance_pdf(request):

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle
    )

    records = Attendance.objects.select_related(
        "employee"
    ).all()

    from_date = request.GET.get(
        "from_date"
    )

    to_date = request.GET.get(
        "to_date"
    )

    employee_id = request.GET.get(
        "employee"
    )

    status = request.GET.get(
        "status"
    )

    if from_date:

        records = records.filter(
            date__gte=from_date
        )

    if to_date:

        records = records.filter(
            date__lte=to_date
        )

    if employee_id:

        records = records.filter(
            employee_id=employee_id
        )

    if status:

        records = records.filter(
            status=status
        )

    records = records.order_by(
        "-date",
        "employee__name"
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="attendance_report.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    data = [
        [
            "Date",
            "Employee",
            "Project",
            "Status",
            "Created By",
            "Updated By",
        ]
    ]

    for record in records:

        data.append(
            [
                str(record.date),
                record.employee.name,
                record.project or "",
                record.get_status_display(),
                (
                    record.created_by.username
                    if record.created_by
                    else ""
                ),
                (
                    record.updated_by.username
                    if record.updated_by
                    else ""
                ),
            ]
        )

    table = Table(
        data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.black
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "LEFT"
                ),
            ]
        )
    )

    doc.build(
        [
            table
        ]
    )

    return response