from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone

from .models import Employee, Attendance

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib.units import mm


# =========================================================
# ATTENDANCE HOME
# =========================================================

@login_required
def attendance_home(request):

    return render(
        request,
        'attendance/attendance_home.html'
    )


# =========================================================
# CHAMARA ATTENDANCE
# =========================================================

@login_required
def employee_attendance(request):

    # Find Chamara
    employee = Employee.objects.filter(
        name__icontains='Chamara'
    ).first()

    if not employee:
        messages.error(
            request,
            'Chamara employee record was not found.'
        )

        return render(
            request,
            'attendance/chamara_attendance.html'
        )

    if request.method == 'POST':

        attendance_date = request.POST.get(
            'attendance_date'
        )

        project = request.POST.get(
            'project',
            ''
        )

        worked = request.POST.get(
            'worked'
        )

        # -------------------------------------------------
        # Validate date
        # -------------------------------------------------

        if not attendance_date:

            messages.error(
                request,
                'Please select a date.'
            )

            return redirect(
                'employee_attendance'
            )

        # -------------------------------------------------
        # Convert attendance status
        # -------------------------------------------------

        if worked == 'Present':

            status = 'WORKED'

        elif worked == 'Absent':

            status = 'NOT_WORKED'

        elif worked == 'Half Day':

            status = 'HALF_DAY'

        else:

            messages.error(
                request,
                'Please select attendance.'
            )

            return redirect(
                'employee_attendance'
            )

        # -------------------------------------------------
        # Project validation
        # -------------------------------------------------

        if status in ['WORKED', 'HALF_DAY']:

            if not project:

                messages.error(
                    request,
                    'Please select a project.'
                )

                return redirect(
                    'employee_attendance'
                )

        else:

            # Absent does not need project
            project = ''

        # -------------------------------------------------
        # CREATE / UPDATE ATTENDANCE
        # -------------------------------------------------

        attendance, created = Attendance.objects.update_or_create(

            employee=employee,

            date=attendance_date,

            defaults={
                'project': project,
                'status': status,
                'note': '',
                'updated_by': request.user,
            }

        )

        # If new record
        if created:

            attendance.created_by = request.user
            attendance.save(
                update_fields=['created_by']
            )

            messages.success(
                request,
                'Attendance saved successfully.'
            )

        else:

            messages.success(
                request,
                'Attendance updated successfully.'
            )

        return redirect(
            'attendance_history'
        )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    return render(
        request,
        'attendance/chamara_attendance.html'
    )


# =========================================================
# NIMALKA ATTENDANCE
# =========================================================

@login_required
def nimalka_attendance(request):

    employee = Employee.objects.filter(
        name__icontains='Nimalka'
    ).first()

    if not employee:

        messages.error(
            request,
            'Nimalka employee record was not found.'
        )

        return render(
            request,
            'attendance/nimalka_attendance.html'
        )

    if request.method == 'POST':

        attendance_date = request.POST.get(
            'attendance_date'
        )

        worked = request.POST.get(
            'worked'
        )

        project = request.POST.get(
            'project',
            ''
        )

        if worked == 'Present':

            status = 'WORKED'

        elif worked == 'Absent':

            status = 'NOT_WORKED'

        elif worked == 'Half Day':

            status = 'HALF_DAY'

        else:

            messages.error(
                request,
                'Please select attendance.'
            )

            return redirect(
                'nimalka_attendance'
            )

        if status in ['WORKED', 'HALF_DAY']:

            if not project:

                messages.error(
                    request,
                    'Please select a project.'
                )

                return redirect(
                    'nimalka_attendance'
                )

        else:

            project = ''

        attendance, created = Attendance.objects.update_or_create(

            employee=employee,

            date=attendance_date,

            defaults={
                'project': project,
                'status': status,
                'note': '',
                'updated_by': request.user,
            }

        )

        if created:

            attendance.created_by = request.user

            attendance.save(
                update_fields=['created_by']
            )

            messages.success(
                request,
                'Nimalka attendance saved successfully.'
            )

        else:

            messages.success(
                request,
                'Nimalka attendance updated successfully.'
            )

        return redirect(
            'attendance_history'
        )

    return render(
        request,
        'attendance/nimalka_attendance.html'
    )


# =========================================================
# LABOUR ATTENDANCE
# =========================================================

@login_required
def labour_attendance(request):

    labour_list = [
        'Labour 01',
        'Labour 02',
        'Labour 03',
        'Labour 04',
        'Labour 05',
    ]

    if request.method == 'POST':

        attendance_date = request.POST.get(
            'attendance_date'
        )

        attendance_data = {}

        for labour in labour_list:

            value = request.POST.get(
                labour.replace(' ', '_')
            )

            attendance_data[labour] = value

        return render(
            request,
            'attendance/labour_attendance.html',
            {
                'labour_list': labour_list,
                'attendance_data': attendance_data,
                'success': True,
                'attendance_date': attendance_date,
            }
        )

    return render(
        request,
        'attendance/labour_attendance.html',
        {
            'labour_list': labour_list,
        }
    )


# =========================================================
# ATTENDANCE HISTORY
# =========================================================

@login_required
def attendance_history(request):

    records = Attendance.objects.select_related(
        'employee',
        'updated_by'
    ).all()

    from_date = request.GET.get(
        'from_date',
        ''
    )

    to_date = request.GET.get(
        'to_date',
        ''
    )

    selected_employee = request.GET.get(
        'employee',
        ''
    )

    selected_status = request.GET.get(
        'status',
        ''
    )

    # -----------------------------------------------------
    # DATE FILTER
    # -----------------------------------------------------

    if from_date:

        records = records.filter(
            date__gte=from_date
        )

    if to_date:

        records = records.filter(
            date__lte=to_date
        )

    # -----------------------------------------------------
    # EMPLOYEE FILTER
    # -----------------------------------------------------

    if selected_employee:

        records = records.filter(
            employee_id=selected_employee
        )

    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if selected_status:

        records = records.filter(
            status=selected_status
        )

    # -----------------------------------------------------
    # ORDER
    # -----------------------------------------------------

    records = records.order_by(
        '-date',
        'employee__name'
    )

    # -----------------------------------------------------
    # EMPLOYEES
    # -----------------------------------------------------

    employees = Employee.objects.filter(
        active=True
    ).order_by(
        'name'
    )

    context = {

        'records': records,

        'employees': employees,

        'from_date': from_date,

        'to_date': to_date,

        'selected_employee':
            selected_employee,

        'selected_status':
            selected_status,
    }

    return render(
        request,
        'attendance/attendance_history.html',
        context
    )


# =========================================================
# ATTENDANCE PDF
# =========================================================

@login_required
def attendance_pdf(request):

    records = Attendance.objects.select_related(
        'employee',
        'updated_by'
    ).all()

    from_date = request.GET.get(
        'from_date',
        ''
    )

    to_date = request.GET.get(
        'to_date',
        ''
    )

    selected_employee = request.GET.get(
        'employee',
        ''
    )

    selected_status = request.GET.get(
        'status',
        ''
    )

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    if from_date:

        records = records.filter(
            date__gte=from_date
        )

    if to_date:

        records = records.filter(
            date__lte=to_date
        )

    if selected_employee:

        records = records.filter(
            employee_id=selected_employee
        )

    if selected_status:

        records = records.filter(
            status=selected_status
        )

    records = records.order_by(
        '-date',
        'employee__name'
    )

    # -----------------------------------------------------
    # PDF RESPONSE
    # -----------------------------------------------------

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        'attachment; '
        'filename="attendance_report.pdf"'
    )

    document = SimpleDocTemplate(

        response,

        pagesize=landscape(A4),

        rightMargin=12 * mm,

        leftMargin=12 * mm,

        topMargin=12 * mm,

        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = styles['Title']

    title_style.alignment = TA_CENTER

    elements = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    elements.append(

        Paragraph(
            'ELV Management System',
            title_style
        )

    )

    elements.append(

        Paragraph(
            'Attendance Report',
            styles['Heading2']
        )

    )

    elements.append(
        Spacer(1, 8)
    )

    # -----------------------------------------------------
    # DATE PERIOD
    # -----------------------------------------------------

    if from_date and to_date:

        period_text = (
            f'<b>Date Period:</b> '
            f'{from_date} to {to_date}'
        )

    elif from_date:

        period_text = (
            f'<b>From Date:</b> '
            f'{from_date}'
        )

    elif to_date:

        period_text = (
            f'<b>Up To Date:</b> '
            f'{to_date}'
        )

    else:

        period_text = (
            '<b>Date Period:</b> '
            'All Dates'
        )

    elements.append(

        Paragraph(
            period_text,
            styles['Normal']
        )

    )

    # -----------------------------------------------------
    # EMPLOYEE
    # -----------------------------------------------------

    employee_name = 'All Employees'

    if selected_employee:

        try:

            employee = Employee.objects.get(
                id=selected_employee
            )

            employee_name = employee.name

        except Employee.DoesNotExist:

            employee_name = 'Unknown'

    elements.append(

        Paragraph(
            f'<b>Employee:</b> '
            f'{employee_name}',
            styles['Normal']
        )

    )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status_name = 'All Status'

    if selected_status == 'WORKED':

        status_name = 'Present'

    elif selected_status == 'NOT_WORKED':

        status_name = 'Absent'

    elif selected_status == 'HALF_DAY':

        status_name = 'Half Day'

    elements.append(

        Paragraph(
            f'<b>Status:</b> '
            f'{status_name}',
            styles['Normal']
        )

    )

    elements.append(
        Spacer(1, 12)
    )

    # -----------------------------------------------------
    # TABLE HEADER
    # -----------------------------------------------------

    data = [

        [
            'Date',
            'Employee',
            'Role',
            'Project',
            'Status',
            'Note',
            'Updated By'
        ]

    ]

    # -----------------------------------------------------
    # TABLE DATA
    # -----------------------------------------------------

    for record in records:

        status_display = (
            record.get_status_display()
        )

        updated_by = '-'

        if record.updated_by:

            updated_by = (
                record.updated_by.username
            )

        note = record.note or '-'

        data.append(

            [
                record.date.strftime(
                    '%Y-%m-%d'
                ),

                record.employee.name,

                record.employee.get_role_display(),

                record.project or '-',

                status_display,

                note,

                updated_by,
            ]

        )

    # -----------------------------------------------------
    # NO RECORDS
    # -----------------------------------------------------

    if len(data) == 1:

        data.append(

            [
                '-',
                'No attendance records found',
                '-',
                '-',
                '-',
                '-',
                '-'
            ]

        )

    # -----------------------------------------------------
    # TABLE
    # -----------------------------------------------------

    table = Table(

        data,

        repeatRows=1,

        colWidths=[

            25 * mm,

            42 * mm,

            25 * mm,

            40 * mm,

            30 * mm,

            60 * mm,

            30 * mm,

        ]

    )

    table.setStyle(

        TableStyle(

            [

                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#212529')
                ),

                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),

                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),

                (
                    'ROWBACKGROUNDS',
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor('#f4f6f8')
                    ]
                ),

                (
                    'LEFTPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    'RIGHTPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),

            ]

        )

    )

    elements.append(table)

    elements.append(
        Spacer(1, 10)
    )

    # -----------------------------------------------------
    # GENERATED TIME
    # -----------------------------------------------------

    generated_time = timezone.localtime().strftime(
        '%Y-%m-%d %H:%M'
    )

    elements.append(

        Paragraph(
            f'Report generated: '
            f'{generated_time}',
            styles['Normal']
        )

    )

    elements.append(

        Paragraph(
            f'Total records: '
            f'{records.count()}',
            styles['Normal']
        )

    )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    document.build(elements)

    return response
