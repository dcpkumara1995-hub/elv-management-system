from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Case, When, IntegerField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Attendance, Employee


# =========================================================
# ATTENDANCE ORDER
# =========================================================

def attendance_employee_order():
    return Case(
        When(
            employee__name__iexact="Chamara Pushpakumara",
            then=1
        ),
        When(
            employee__name__iexact="Nimalka",
            then=2
        ),
        When(
            employee__name__iexact="Asika",
            then=3
        ),
        When(
            employee__name__iexact="Dikwella",
            then=4
        ),
        When(
            employee__name__iexact="Jayampathe",
            then=5
        ),
        When(
            employee__name__iexact="Kaveen",
            then=6
        ),
        When(
            employee__name__iexact="Nipuna",
            then=7
        ),
        default=99,
        output_field=IntegerField(),
    )


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

        return redirect(
            "attendance_home"
        )

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
# DELETE ATTENDANCE
# SUPER ADMIN ONLY
# =========================================================

@login_required
def delete_attendance(request, attendance_id):

    if not request.user.is_superuser:

        raise PermissionDenied

    attendance = get_object_or_404(
        Attendance,
        id=attendance_id
    )

    if request.method != "POST":

        return redirect(
            "attendance_history"
        )

    employee_name = attendance.employee.name
    attendance_date = attendance.date

    attendance.delete()

    messages.success(
        request,
        f"Attendance for {employee_name} on {attendance_date} deleted successfully."
    )

    return redirect(
        "attendance_history"
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
        attendance_employee_order(),
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
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle
    )
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        KeepTogether,
    )

    # -----------------------------------------------------
    # GET FILTERS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # APPLY FILTERS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # SAME ORDER AS ATTENDANCE HISTORY
    # -----------------------------------------------------

    records = records.order_by(
        "-date",
        attendance_employee_order(),
        "employee__name"
    )

    records_list = list(records)

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="attendance_report.pdf"'

    # -----------------------------------------------------
    # A4 PORTRAIT
    # -----------------------------------------------------

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32,
        title="Attendance Report",
    )

    # -----------------------------------------------------
    # COLORS
    # -----------------------------------------------------

    dark_blue = colors.HexColor("#0B3D91")
    blue = colors.HexColor("#1976D2")

    light_blue = colors.HexColor("#EAF3FF")
    very_light_blue = colors.HexColor("#F7FBFF")
    border_blue = colors.HexColor("#B8D4F0")

    text_dark = colors.HexColor("#1F2937")
    text_gray = colors.HexColor("#6B7280")

    # Status text colors ONLY
    green = colors.HexColor("#198754")
    orange = colors.HexColor("#F59E0B")
    red = colors.HexColor("#DC3545")

    # Holiday row colors
    poya_yellow = colors.HexColor("#FFF3B0")
    weekend_blue = colors.HexColor("#DDEEFF")

    white = colors.white

    # -----------------------------------------------------
    # STYLES
    # -----------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AttendanceTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=white,
        alignment=TA_CENTER,
        spaceAfter=0,
    )

    subtitle_style = ParagraphStyle(
        "AttendanceSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=white,
        alignment=TA_CENTER,
    )

    info_label_style = ParagraphStyle(
        "InfoLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=dark_blue,
    )

    info_value_style = ParagraphStyle(
        "InfoValue",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=text_dark,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=white,
        alignment=TA_CENTER,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=text_dark,
    )

    date_cell_style = ParagraphStyle(
        "DateCell",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
    )

    status_style = ParagraphStyle(
        "Status",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
    )

    summary_title_style = ParagraphStyle(
        "SummaryTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=dark_blue,
    )

    summary_value_style = ParagraphStyle(
        "SummaryValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=text_dark,
        alignment=TA_CENTER,
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        textColor=text_gray,
        alignment=TA_CENTER,
    )

    # -----------------------------------------------------
    # EMPLOYEE NAME
    # -----------------------------------------------------

    selected_employee_name = None

    if employee_id:

        selected_employee = Employee.objects.filter(
            id=employee_id
        ).first()

        if selected_employee:

            selected_employee_name = (
                selected_employee.name
            )

    if not selected_employee_name:

        employee_names = list(
            records.values_list(
                "employee__name",
                flat=True
            ).distinct()
        )

        if len(employee_names) == 1:

            selected_employee_name = (
                employee_names[0]
            )

    if not selected_employee_name:

        selected_employee_name = "All Employees"

    # -----------------------------------------------------
    # DATE RANGE
    # -----------------------------------------------------

    if from_date and to_date:

        period_text = (
            f"From: {from_date}    |    To: {to_date}"
        )

    elif from_date:

        period_text = (
            f"From: {from_date}    |    To: All Dates"
        )

    elif to_date:

        period_text = (
            f"From: All Dates    |    To: {to_date}"
        )

    else:

        period_text = "All Dates"

    # -----------------------------------------------------
    # 2026 SRI LANKA POYA DAYS
    # -----------------------------------------------------

    poya_days = {

        "2026-01-03": "Duruthu Full Moon Poya Day",

        "2026-02-01": "Navam Full Moon Poya Day",

        "2026-03-02": "Medin Full Moon Poya Day",

        "2026-04-01": "Bak Full Moon Poya Day",

        "2026-05-01": "Vesak Full Moon Poya Day",

        "2026-05-30": "Adhi Poson Full Moon Poya Day",

        "2026-06-29": "Poson Full Moon Poya Day",

        "2026-07-29": "Esala Full Moon Poya Day",

        "2026-08-27": "Nikini Full Moon Poya Day",

        "2026-09-26": "Binara Full Moon Poya Day",

        "2026-10-25": "Vap Full Moon Poya Day",

        "2026-11-24": "Il Full Moon Poya Day",

        "2026-12-23": "Unduvap Full Moon Poya Day",
    }

    # -----------------------------------------------------
    # DATE RANGE FOR HOLIDAY INSERTION
    # -----------------------------------------------------

    holiday_start = None
    holiday_end = None

    try:

        if from_date:

            holiday_start = datetime.strptime(
                from_date,
                "%Y-%m-%d"
            ).date()

        if to_date:

            holiday_end = datetime.strptime(
                to_date,
                "%Y-%m-%d"
            ).date()

        # Only From date
        if holiday_start and not holiday_end:

            if records_list:

                holiday_end = max(
                    record.date
                    for record in records_list
                )

        # Only To date
        if holiday_end and not holiday_start:

            if records_list:

                holiday_start = min(
                    record.date
                    for record in records_list
                )

        # No date filters
        if not holiday_start and not holiday_end:

            if records_list:

                holiday_start = min(
                    record.date
                    for record in records_list
                )

                holiday_end = max(
                    record.date
                    for record in records_list
                )

    except (ValueError, TypeError):

        holiday_start = None
        holiday_end = None

    # -----------------------------------------------------
    # DATE -> RECORDS MAP
    # -----------------------------------------------------

    records_by_date = {}

    for record in records_list:

        records_by_date.setdefault(
            record.date,
            []
        ).append(record)

    # -----------------------------------------------------
    # COMPLETE DATE LIST
    # -----------------------------------------------------

    report_dates = set(
        record.date
        for record in records_list
    )

    if holiday_start and holiday_end:

        current_date = holiday_start

        while current_date <= holiday_end:

            report_dates.add(
                current_date
            )

            current_date += timedelta(
                days=1
            )

    report_dates = sorted(
        report_dates,
        reverse=True
    )

    # -----------------------------------------------------
    # MAIN STORY
    # -----------------------------------------------------

    story = []

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    header_table = Table(
        [
            [
                Paragraph(
                    "ATTENDANCE REPORT",
                    title_style
                )
            ]
        ],
        colWidths=[
            doc.width
        ],
    )

    header_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    dark_blue
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    13
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    5
                ),
                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, 1),
                    2
                ),
                (
                    "BOTTOMPADDING",
                    (0, 1),
                    (-1, 1),
                    12
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    dark_blue
                ),
            ]
        )
    )

    story.append(
        header_table
    )

    story.append(
        Spacer(1, 12)
    )

    # -----------------------------------------------------
    # REPORT INFORMATION
    # -----------------------------------------------------

    info_table = Table(
        [
            [
                Paragraph(
                    "EMPLOYEE",
                    info_label_style
                ),
                Paragraph(
                    selected_employee_name,
                    info_value_style
                ),
            ],
            [
                Paragraph(
                    "PERIOD",
                    info_label_style
                ),
                Paragraph(
                    period_text,
                    info_value_style
                ),
            ],
        ],
        colWidths=[
            85,
            doc.width - 85
        ],
    )

    info_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    light_blue
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    border_blue
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    border_blue
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ]
        )
    )

    story.append(
        info_table
    )

    story.append(
        Spacer(1, 15)
    )

    # -----------------------------------------------------
    # STATUS DISPLAY
    # -----------------------------------------------------

    def status_text(record_status):

        if record_status == "WORKED":

            return "Worked"

        if record_status == "HALF_DAY":

            return "Half Day"

        if record_status == "NOT_WORKED":

            return "Not Worked"

        return str(
            record_status
        ).replace(
            "_",
            " "
        ).title()

    # -----------------------------------------------------
    # ATTENDANCE TABLE
    # -----------------------------------------------------

    data = [
        [
            Paragraph(
                "DATE",
                table_header_style
            ),
            Paragraph(
                "PROJECT",
                table_header_style
            ),
            Paragraph(
                "STATUS",
                table_header_style
            ),
        ]
    ]

    worked_count = 0
    half_day_count = 0
    not_worked_count = 0

    # Keep row number -> holiday type
    holiday_rows = {}

    # -----------------------------------------------------
    # BUILD REPORT ROWS
    # -----------------------------------------------------

    for report_date in report_dates:

        date_records = records_by_date.get(
            report_date,
            []
        )

        date_string = report_date.strftime(
            "%Y-%m-%d"
        )

        is_poya = date_string in poya_days

        is_saturday = (
            report_date.weekday() == 5
        )

        is_sunday = (
            report_date.weekday() == 6
        )

        # -------------------------------------------------
        # ATTENDANCE RECORDS
        # -------------------------------------------------

        if date_records:

            for record in date_records:

                # Count real attendance records only
                if record.status == "WORKED":

                    worked_count += 1

                elif record.status == "HALF_DAY":

                    half_day_count += 1

                elif record.status == "NOT_WORKED":

                    not_worked_count += 1

                display_status = status_text(
                    record.status
                )

                # -------------------------------------------------
                # STATUS LETTER COLOR ONLY
                # -------------------------------------------------

                if record.status == "WORKED":

                    status_color = green

                elif record.status == "HALF_DAY":

                    status_color = orange

                elif record.status == "NOT_WORKED":

                    status_color = red

                else:

                    status_color = dark_blue

                status_paragraph = Paragraph(
                    f'<font color="{status_color.hexval()}">'
                    f'<b>{display_status}</b>'
                    f'</font>',
                    status_style
                )

                data.append(
                    [
                        Paragraph(
                            str(record.date),
                            date_cell_style
                        ),
                        Paragraph(
                            record.project or "-",
                            table_cell_style
                        ),
                        status_paragraph,
                    ]
                )

                current_row = len(data) - 1

                # -------------------------------------------------
                # HOLIDAY ROW COLOR
                # -------------------------------------------------
                #
                # Poya has priority over Saturday / Sunday.
                #

                if is_poya:

                    holiday_rows[current_row] = "POYA"

                elif is_saturday or is_sunday:

                    holiday_rows[current_row] = "WEEKEND"

        # -----------------------------------------------------
        # NO ATTENDANCE RECORD
        # -----------------------------------------------------

        else:

            # Add blank row only for
            # Poya / Saturday / Sunday
            if is_poya or is_saturday or is_sunday:

                data.append(
                    [
                        Paragraph(
                            str(report_date),
                            date_cell_style
                        ),
                        Paragraph(
                            "",
                            table_cell_style
                        ),
                        Paragraph(
                            "",
                            status_style
                        ),
                    ]
                )

                current_row = len(data) - 1

                if is_poya:

                    holiday_rows[current_row] = "POYA"

                else:

                    holiday_rows[current_row] = "WEEKEND"

    # -----------------------------------------------------
    # EMPTY REPORT
    # -----------------------------------------------------

    if len(data) == 1:

        data.append(
            [
                Paragraph(
                    "-",
                    table_cell_style
                ),
                Paragraph(
                    "No attendance records found",
                    table_cell_style
                ),
                Paragraph(
                    "-",
                    table_cell_style
                ),
            ]
        )

    # -----------------------------------------------------
    # TABLE
    # -----------------------------------------------------

    attendance_table = Table(
        data,
        colWidths=[
            95,
            doc.width - 95 - 95,
            95,
        ],
        repeatRows=1,
        hAlign="LEFT",
    )

    table_style_commands = [

        # Header
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            blue
        ),

        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            white
        ),

        # Borders
        (
            "BOX",
            (0, 0),
            (-1, -1),
            0.7,
            border_blue
        ),

        (
            "INNERGRID",
            (0, 0),
            (-1, -1),
            0.4,
            border_blue
        ),

        # Alignment
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        (
            "ALIGN",
            (0, 0),
            (0, -1),
            "CENTER"
        ),

        (
            "ALIGN",
            (2, 0),
            (2, -1),
            "CENTER"
        ),

        # Padding
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, 0),
            8
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, 0),
            8
        ),

        (
            "TOPPADDING",
            (0, 1),
            (-1, -1),
            7
        ),

        (
            "BOTTOMPADDING",
            (0, 1),
            (-1, -1),
            7
        ),
    ]

    # -----------------------------------------------------
    # NORMAL ROW COLORS
    # -----------------------------------------------------

    for row_number in range(
        1,
        len(data)
    ):

        # Holiday rows handled separately
        if row_number in holiday_rows:

            continue

        if row_number % 2 == 1:

            table_style_commands.append(
                (
                    "BACKGROUND",
                    (0, row_number),
                    (-1, row_number),
                    white
                )
            )

        else:

            table_style_commands.append(
                (
                    "BACKGROUND",
                    (0, row_number),
                    (-1, row_number),
                    very_light_blue
                )
            )

    # -----------------------------------------------------
    # HOLIDAY COLORS
    # -----------------------------------------------------
    #
    # Poya = Light Yellow
    # Saturday/Sunday = Light Blue
    #
    # Poya has priority.
    # -----------------------------------------------------

    for row_number, holiday_type in holiday_rows.items():

        if holiday_type == "POYA":

            table_style_commands.append(
                (
                    "BACKGROUND",
                    (0, row_number),
                    (-1, row_number),
                    poya_yellow
                )
            )

        elif holiday_type == "WEEKEND":

            table_style_commands.append(
                (
                    "BACKGROUND",
                    (0, row_number),
                    (-1, row_number),
                    weekend_blue
                )
            )

    # -----------------------------------------------------
    # IMPORTANT
    #
    # NO STATUS CELL BACKGROUND COLOR.
    #
    # Worked / Half Day / Not Worked
    # are colored ONLY in their letters.
    # -----------------------------------------------------

    attendance_table.setStyle(
        TableStyle(
            table_style_commands
        )
    )

    story.append(
        attendance_table
    )

    story.append(
        Spacer(1, 15)
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    total_records = (
        worked_count
        + half_day_count
        + not_worked_count
    )

    summary_table = Table(
        [
            [
                Paragraph(
                    "WORKED",
                    summary_title_style
                ),
                Paragraph(
                    "HALF DAY",
                    summary_title_style
                ),
                Paragraph(
                    "NOT WORKED",
                    summary_title_style
                ),
                Paragraph(
                    "TOTAL",
                    summary_title_style
                ),
            ],
            [
                Paragraph(
                    str(worked_count),
                    summary_value_style
                ),
                Paragraph(
                    str(half_day_count),
                    summary_value_style
                ),
                Paragraph(
                    str(not_worked_count),
                    summary_value_style
                ),
                Paragraph(
                    str(total_records),
                    summary_value_style
                ),
            ],
        ],
        colWidths=[
            doc.width / 4,
            doc.width / 4,
            doc.width / 4,
            doc.width / 4,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    light_blue
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    very_light_blue
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    border_blue
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    border_blue
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
            ]
        )
    )

    story.append(
        KeepTogether(
            [
                Paragraph(
                    "ATTENDANCE SUMMARY",
                    summary_title_style
                ),
                Spacer(1, 5),
                summary_table,
            ]
        )
    )

    story.append(
        Spacer(1, 14)
    )

    story.append(
        Paragraph(
            "Generated by ELV Management System",
            footer_style
        )
    )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    doc.build(
        story
    )

    return response