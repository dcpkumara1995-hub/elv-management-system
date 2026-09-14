from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

from .models import DailyWork
from attendance.models import Attendance


# =========================================================
# DAILY WORK LIST
# =========================================================

@login_required
def daily_work_list(request):

    works = DailyWork.objects.select_related(
        "created_by"
    ).order_by(
        "-date",
        "-created_at",
    )

    return render(
        request,
        "dailyworks/daily_work_list.html",
        {
            "works": works,
        },
    )


# =========================================================
# ADD DAILY WORK
# =========================================================

@login_required
def daily_work_add(request):

    if request.method == "POST":

        work_date = request.POST.get("date")
        work_items = request.POST.getlist("work")

        valid_items = []

        for item in work_items:

            item = item.strip()

            if item:
                valid_items.append(item)

        if not work_date:

            messages.error(
                request,
                "Please select a date.",
            )

            return redirect(
                "daily_work_add"
            )

        if not valid_items:

            messages.error(
                request,
                "Please enter at least one work item.",
            )

            return redirect(
                "daily_work_add"
            )

        for item in valid_items:

            DailyWork.objects.create(
                date=work_date,
                work=item,
                created_by=request.user,
            )

        messages.success(
            request,
            "Daily work saved successfully.",
        )

        return redirect(
            "daily_work_list"
        )

    return render(
        request,
        "dailyworks/daily_work_add.html",
    )


# =========================================================
# EDIT DAILY WORK
# =========================================================

@login_required
def daily_work_edit(request, work_id):

    work = get_object_or_404(
        DailyWork,
        id=work_id,
    )

    if request.method == "POST":

        work_date = request.POST.get("date")

        work_text = request.POST.get(
            "work",
            "",
        ).strip()

        if not work_date or not work_text:

            messages.error(
                request,
                "Date and work are required.",
            )

            return redirect(
                "daily_work_edit",
                work_id=work.id,
            )

        work.date = work_date
        work.work = work_text

        work.save()

        messages.success(
            request,
            "Daily work updated successfully.",
        )

        return redirect(
            "daily_work_list"
        )

    return render(
        request,
        "dailyworks/daily_work_edit.html",
        {
            "work": work,
        },
    )


# =========================================================
# DELETE DAILY WORK
# =========================================================

@login_required
def daily_work_delete(request, work_id):

    work = get_object_or_404(
        DailyWork,
        id=work_id,
    )

    if request.method == "POST":

        work.delete()

        messages.success(
            request,
            "Daily work deleted successfully.",
        )

    return redirect(
        "daily_work_list"
    )


# =========================================================
# DAILY WORK REPORT PAGE
# =========================================================

@login_required
def daily_work_report(request):

    works = DailyWork.objects.all().order_by(
        "-date",
        "-created_at",
    )

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    if start_date:

        works = works.filter(
            date__gte=start_date,
        )

    if end_date:

        works = works.filter(
            date__lte=end_date,
        )

    return render(
        request,
        "dailyworks/daily_work_report.html",
        {
            "works": works,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


# =========================================================
# CLEAN WORK TEXT
# =========================================================

def clean_work_text(text):

    if not text:
        return ""

    text = text.replace(
        "<br>",
        "\n",
    )

    text = text.replace(
        "<br/>",
        "\n",
    )

    text = text.replace(
        "<br />",
        "\n",
    )

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


# =========================================================
# FORMAT WORK DESCRIPTION
# =========================================================

def format_work_description(text):

    text = clean_work_text(
        text
    )

    if not text:
        return ""

    replacements = [
        ("CCTV POINTS", "CCTV points"),
        ("CCTV POINT", "CCTV point"),
        ("DATA POINTS", "Data points"),
        ("DATA POINT", "Data point"),
        ("WIFI POINTS", "WiFi points"),
        ("WIFI POINT", "WiFi point"),
        ("RFID POINTS", "RFID points"),
        ("RFID POINT", "RFID point"),
        ("VOICE CONTROLLER", "Voice Controller"),
        ("SUNBOX", "Sunbox"),
        ("1F", "1F"),
        ("2F", "2F"),
        ("3F", "3F"),
        ("4F", "4F"),
    ]

    for old, new in replacements:

        text = text.replace(
            old,
            new,
        )

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        lines.append(line)

    return "\n".join(lines)


# =========================================================
# DAILY WORK PDF
# =========================================================

@login_required
def daily_work_pdf(request):

    works = DailyWork.objects.all().order_by(
        "date",
        "created_at",
    )

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    if start_date:

        works = works.filter(
            date__gte=start_date,
        )

    if end_date:

        works = works.filter(
            date__lte=end_date,
        )

    response = HttpResponse(
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        'attachment; filename="daily_work_report.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    title_style = ParagraphStyle(
        "PDFTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    normal_style = ParagraphStyle(
        "Normal",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
    )

    heading_style = ParagraphStyle(
        "Heading",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
    )

    story = []

    story.append(
        Paragraph(
            "DAILY WORK REPORT",
            title_style,
        )
    )

    period_text = ""

    if start_date and end_date:

        period_text = (
            f"Period: {start_date} to {end_date}"
        )

    elif start_date:

        period_text = (
            f"From: {start_date}"
        )

    elif end_date:

        period_text = (
            f"Up to: {end_date}"
        )

    if period_text:

        story.append(
            Paragraph(
                period_text,
                normal_style,
            )
        )

        story.append(
            Spacer(
                1,
                8,
            )
        )

    table_data = [
        [
            Paragraph(
                "Date",
                heading_style,
            ),
            Paragraph(
                "Work",
                heading_style,
            ),
        ]
    ]

    for work in works:

        formatted_work = format_work_description(
            work.work
        )

        work_paragraph = Paragraph(
            formatted_work.replace(
                "\n",
                "<br/>",
            ),
            normal_style,
        )

        table_data.append(
            [
                Paragraph(
                    str(work.date),
                    normal_style,
                ),
                work_paragraph,
            ]
        )

    if len(table_data) == 1:

        table_data.append(
            [
                Paragraph(
                    "-",
                    normal_style,
                ),
                Paragraph(
                    "No daily work records found.",
                    normal_style,
                ),
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            35 * mm,
            137 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#0d6efd"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(
        table
    )

    document.build(
        story
    )

    return response


# =========================================================
# DAILY REPORT PAGE
# =========================================================

@login_required
def daily_report(request):

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    works = DailyWork.objects.all().order_by(
        "date",
        "created_at",
    )

    attendance_records = Attendance.objects.filter(
        employee__role="LABOUR",
        status="WORKED",
    ).select_related(
        "employee",
    ).order_by(
        "date",
        "employee__name",
    )

    # -----------------------------------------------------
    # DATE FILTER
    # -----------------------------------------------------

    if start_date:

        works = works.filter(
            date__gte=start_date,
        )

        attendance_records = attendance_records.filter(
            date__gte=start_date,
        )

    if end_date:

        works = works.filter(
            date__lte=end_date,
        )

        attendance_records = attendance_records.filter(
            date__lte=end_date,
        )

    # -----------------------------------------------------
    # WORK BY DATE
    # -----------------------------------------------------

    work_by_date = {}

    for work in works:

        if work.date not in work_by_date:

            work_by_date[work.date] = []

        formatted = format_work_description(
            work.work
        )

        if formatted:

            work_by_date[work.date].append(
                formatted
            )

    # -----------------------------------------------------
    # LABOUR BY DATE
    # -----------------------------------------------------

    attendance_by_date = {}

    for record in attendance_records:

        if record.date not in attendance_by_date:

            attendance_by_date[record.date] = []

        employee_name = record.employee.name

        if employee_name not in attendance_by_date[
            record.date
        ]:

            attendance_by_date[
                record.date
            ].append(
                employee_name
            )

    # -----------------------------------------------------
    # ALL DATES
    # -----------------------------------------------------

    all_dates = sorted(
        set(work_by_date.keys())
        | set(attendance_by_date.keys())
    )

    # -----------------------------------------------------
    # REPORT DATA
    # -----------------------------------------------------

    report_data = []

    total_labour_days = 0

    for report_date in all_dates:

        labour_names = attendance_by_date.get(
            report_date,
            [],
        )

        work_items = work_by_date.get(
            report_date,
            [],
        )

        total_labors = len(
            labour_names
        )

        total_labour_days += total_labors

        report_data.append(
            {
                "project": "IIT Project",
                "date": report_date,
                "total_labors": total_labors,
                "labors_name": ", ".join(
                    labour_names
                ),
                "work": "\n".join(
                    work_items
                ),
            }
        )

    # -----------------------------------------------------
    # PAGE
    # -----------------------------------------------------

    return render(
        request,
        "dailyworks/daily_report.html",
        {
            "report_data": report_data,
            "start_date": start_date,
            "end_date": end_date,
            "total_labour_days": total_labour_days,
        },
    )


# =========================================================
# DAILY REPORT PDF
# =========================================================

@login_required
def daily_report_pdf(request):

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    works = DailyWork.objects.all().order_by(
        "date",
        "created_at",
    )

    attendance_records = Attendance.objects.filter(
        employee__role="LABOUR",
        status="WORKED",
    ).select_related(
        "employee",
    ).order_by(
        "date",
        "employee__name",
    )

    # -----------------------------------------------------
    # DATE FILTER
    # -----------------------------------------------------

    if start_date:

        works = works.filter(
            date__gte=start_date,
        )

        attendance_records = attendance_records.filter(
            date__gte=start_date,
        )

    if end_date:

        works = works.filter(
            date__lte=end_date,
        )

        attendance_records = attendance_records.filter(
            date__lte=end_date,
        )

    # -----------------------------------------------------
    # WORK BY DATE
    # -----------------------------------------------------

    work_by_date = {}

    for work in works:

        if work.date not in work_by_date:

            work_by_date[work.date] = []

        formatted = format_work_description(
            work.work
        )

        if formatted:

            work_by_date[work.date].append(
                formatted
            )

    # -----------------------------------------------------
    # LABOUR BY DATE
    # -----------------------------------------------------

    attendance_by_date = {}

    for record in attendance_records:

        if record.date not in attendance_by_date:

            attendance_by_date[record.date] = []

        employee_name = record.employee.name

        if employee_name not in attendance_by_date[
            record.date
        ]:

            attendance_by_date[
                record.date
            ].append(
                employee_name
            )

    # -----------------------------------------------------
    # ALL DATES
    # -----------------------------------------------------

    all_dates = sorted(
        set(work_by_date.keys())
        | set(attendance_by_date.keys())
    )

    # -----------------------------------------------------
    # PDF RESPONSE
    # -----------------------------------------------------

    response = HttpResponse(
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        'attachment; filename="iit_daily_report.pdf"'
    )

    # -----------------------------------------------------
    # A4 PORTRAIT
    # -----------------------------------------------------

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="IIT PROJECT - DAILY REPORT",
    )

    # -----------------------------------------------------
    # PDF STYLES
    # -----------------------------------------------------

    title_style = ParagraphStyle(
        "DailyReportTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    )

    period_style = ParagraphStyle(
        "DailyReportPeriod",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#555555"
        ),
        spaceAfter=7 * mm,
    )

    date_style = ParagraphStyle(
        "DailyReportDate",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.white,
    )

    label_style = ParagraphStyle(
        "DailyReportLabel",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
    )

    value_style = ParagraphStyle(
        "DailyReportValue",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        wordWrap="CJK",
    )

    work_title_style = ParagraphStyle(
        "DailyReportWorkTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
        textColor=colors.HexColor(
            "#0d6efd"
        ),
        spaceAfter=3 * mm,
    )

    work_style = ParagraphStyle(
        "DailyReportWork",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        wordWrap="CJK",
    )

    summary_style = ParagraphStyle(
        "DailyReportSummary",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#084298"
        ),
    )

    empty_style = ParagraphStyle(
        "DailyReportEmpty",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#666666"
        ),
    )

    # -----------------------------------------------------
    # STORY
    # -----------------------------------------------------

    story = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "IIT PROJECT - DAILY REPORT",
            title_style,
        )
    )

    # -----------------------------------------------------
    # PERIOD
    # -----------------------------------------------------

    if start_date and end_date:

        period_text = (
            f"Period: {start_date} to {end_date}"
        )

    elif start_date:

        period_text = (
            f"From: {start_date}"
        )

    elif end_date:

        period_text = (
            f"Up to: {end_date}"
        )

    else:

        period_text = "All Records"

    story.append(
        Paragraph(
            period_text,
            period_style,
        )
    )

    # -----------------------------------------------------
    # DAILY DATE SECTIONS
    # -----------------------------------------------------

    if all_dates:

        total_labour_days = 0

        for report_date in all_dates:

            labour_names = attendance_by_date.get(
                report_date,
                [],
            )

            work_items = work_by_date.get(
                report_date,
                [],
            )

            total_labours = len(
                labour_names
            )

            # -------------------------------------------------
            # KEEP EXISTING CALCULATION
            # -------------------------------------------------

            total_labour_days += total_labours

            # -------------------------------------------------
            # DAILY SECTION
            # -------------------------------------------------

            daily_section = []

            # -------------------------------------------------
            # DATE HEADER
            # -------------------------------------------------

            date_header = Table(
                [
                    [
                        Paragraph(
                            report_date.strftime(
                                "%Y-%m-%d"
                            ),
                            date_style,
                        )
                    ]
                ],
                colWidths=[
                    182 * mm
                ],
            )

            date_header.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor(
                                "#0d6efd"
                            ),
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            9,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            9,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                    ]
                )
            )

            daily_section.append(
                date_header
            )

            # -------------------------------------------------
            # TOTAL LABORS
            # -------------------------------------------------

            total_table = Table(
                [
                    [
                        Paragraph(
                            "Total Labors:",
                            label_style,
                        ),
                        Paragraph(
                            str(total_labours),
                            value_style,
                        ),
                    ]
                ],
                colWidths=[
                    45 * mm,
                    137 * mm,
                ],
            )

            total_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (0, 0),
                            colors.HexColor(
                                "#f3f4f6"
                            ),
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor(
                                "#d5d5d5"
                            ),
                        ),
                        (
                            "INNERGRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor(
                                "#d5d5d5"
                            ),
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                    ]
                )
            )

            daily_section.append(
                total_table
            )

            # -------------------------------------------------
            # LABORS
            # -------------------------------------------------

            if labour_names:

                labour_text = ", ".join(
                    labour_names
                )

            else:

                labour_text = "-"

            labour_table = Table(
                [
                    [
                        Paragraph(
                            "Labors:",
                            label_style,
                        ),
                        Paragraph(
                            labour_text,
                            value_style,
                        ),
                    ]
                ],
                colWidths=[
                    45 * mm,
                    137 * mm,
                ],
            )

            labour_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (0, 0),
                            colors.HexColor(
                                "#f3f4f6"
                            ),
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor(
                                "#d5d5d5"
                            ),
                        ),
                        (
                            "INNERGRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor(
                                "#d5d5d5"
                            ),
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                    ]
                )
            )

            daily_section.append(
                labour_table
            )

            # -------------------------------------------------
            # WORK DETAILS
            # -------------------------------------------------

            daily_section.append(
                Spacer(
                    1,
                    5 * mm,
                )
            )

            daily_section.append(
                Paragraph(
                    "WORK DETAILS",
                    work_title_style,
                )
            )

            if work_items:

                work_flowables = []

                work_number = 1

                for work_item in work_items:

                    safe_text = (
                        work_item
                        .replace(
                            "&",
                            "&amp;",
                        )
                        .replace(
                            "<",
                            "&lt;",
                        )
                        .replace(
                            ">",
                            "&gt;",
                        )
                    )

                    safe_text = safe_text.replace(
                        "\n",
                        "<br/>",
                    )

                    work_flowables.append(
                        Paragraph(
                            (
                                f"<b>{work_number}.</b> "
                                f"{safe_text}"
                            ),
                            work_style,
                        )
                    )

                    work_flowables.append(
                        Spacer(
                            1,
                            3 * mm,
                        )
                    )

                    work_number += 1

                work_table = Table(
                    [
                        [
                            work_flowables
                        ]
                    ],
                    colWidths=[
                        182 * mm
                    ],
                )

                work_table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, -1),
                                colors.HexColor(
                                    "#fafafa"
                                ),
                            ),
                            (
                                "BOX",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.HexColor(
                                    "#d5d5d5"
                                ),
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP",
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                9,
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                9,
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                8,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                        ]
                    )
                )

                daily_section.append(
                    work_table
                )

            else:

                no_work_table = Table(
                    [
                        [
                            Paragraph(
                                "-",
                                value_style,
                            )
                        ]
                    ],
                    colWidths=[
                        182 * mm
                    ],
                )

                no_work_table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, -1),
                                colors.HexColor(
                                    "#fafafa"
                                ),
                            ),
                            (
                                "BOX",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.HexColor(
                                    "#d5d5d5"
                                ),
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                9,
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                9,
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                8,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                8,
                            ),
                        ]
                    )
                )

                daily_section.append(
                    no_work_table
                )

            # -------------------------------------------------
            # SPACE BETWEEN DATE SECTIONS
            # -------------------------------------------------

            daily_section.append(
                Spacer(
                    1,
                    8 * mm,
                )
            )

            # -------------------------------------------------
            # KEEP DATE SECTION TOGETHER
            # -------------------------------------------------

            story.append(
                KeepTogether(
                    daily_section
                )
            )

    else:

        story.append(
            Spacer(
                1,
                10 * mm,
            )
        )

        story.append(
            Paragraph(
                "No daily report records found.",
                empty_style,
            )
        )

        total_labour_days = 0

    # -----------------------------------------------------
    # TOTAL LABOUR DAYS
    # -----------------------------------------------------

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    summary_table = Table(
        [
            [
                Paragraph(
                    (
                        "TOTAL LABOUR DAYS WORKED: "
                        f"{total_labour_days}"
                    ),
                    summary_style,
                )
            ]
        ],
        colWidths=[
            182 * mm
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#cfe2ff"
                    ),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor(
                        "#9ec5fe"
                    ),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(
        summary_table
    )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    document.build(
        story
    )

    return response