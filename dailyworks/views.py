from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .models import DailyWork


@login_required(login_url="/login/")
def daily_work_list(request):

    works = DailyWork.objects.select_related(
        "created_by"
    ).all()

    return render(
        request,
        "dailyworks/daily_work_list.html",
        {
            "works": works
        }
    )


@login_required(login_url="/login/")
def daily_work_add(request):

    if request.method == "POST":

        work_date = request.POST.get("date")

        work_items = request.POST.getlist("work")

        work_items = [
            work.strip()
            for work in work_items
            if work.strip()
        ]

        if not work_date:

            messages.error(
                request,
                "Please select a date."
            )

            return redirect("daily_work_add")

        if not work_items:

            messages.error(
                request,
                "Please enter at least one work item."
            )

            return redirect("daily_work_add")

        for work_item in work_items:

            DailyWork.objects.create(
                date=work_date,
                work=work_item,
                created_by=request.user
            )

        messages.success(
            request,
            "Daily work items saved successfully."
        )

        return redirect("daily_work_list")

    return render(
        request,
        "dailyworks/daily_work_add.html"
    )


@login_required(login_url="/login/")
def daily_work_edit(request, work_id):

    daily_work = get_object_or_404(
        DailyWork,
        id=work_id
    )

    if request.method == "POST":

        work_date = request.POST.get("date")

        work_text = request.POST.get(
            "work",
            ""
        ).strip()

        if not work_date or not work_text:

            messages.error(
                request,
                "Date and work are required."
            )

            return redirect(
                "daily_work_edit",
                work_id=work_id
            )

        daily_work.date = work_date
        daily_work.work = work_text

        daily_work.save()

        messages.success(
            request,
            "Daily work updated successfully."
        )

        return redirect(
            "daily_work_list"
        )

    return render(
        request,
        "dailyworks/daily_work_edit.html",
        {
            "daily_work": daily_work
        }
    )


@login_required(login_url="/login/")
def daily_work_delete(request, work_id):

    daily_work = get_object_or_404(
        DailyWork,
        id=work_id
    )

    if request.method == "POST":

        daily_work.delete()

        messages.success(
            request,
            "Daily work deleted successfully."
        )

    return redirect(
        "daily_work_list"
    )


@login_required(login_url="/login/")
def daily_work_report(request):

    from_date = request.GET.get(
        "from_date",
        ""
    )

    to_date = request.GET.get(
        "to_date",
        ""
    )

    works = DailyWork.objects.select_related(
        "created_by"
    ).all()

    if from_date:

        works = works.filter(
            date__gte=from_date
        )

    if to_date:

        works = works.filter(
            date__lte=to_date
        )

    return render(
        request,
        "dailyworks/daily_work_report.html",
        {
            "works": works,
            "from_date": from_date,
            "to_date": to_date
        }
    )


@login_required(login_url="/login/")
def daily_work_pdf(request):

    from_date = request.GET.get(
        "from_date",
        ""
    )

    to_date = request.GET.get(
        "to_date",
        ""
    )

    works = DailyWork.objects.select_related(
        "created_by"
    ).all()

    if from_date:

        works = works.filter(
            date__gte=from_date
        )

    if to_date:

        works = works.filter(
            date__lte=to_date
        )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'inline; filename="daily_work_report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "IIT PROJECT - DAILY WORK REPORT",
            styles["Title"]
        )
    )

    elements.append(
        Spacer(
            1,
            8
        )
    )

    if from_date or to_date:

        period_text = (
            "Period: "
            + (from_date if from_date else "All")
            + " to "
            + (to_date if to_date else "All")
        )

        elements.append(
            Paragraph(
                period_text,
                styles["Normal"]
            )
        )

        elements.append(
            Spacer(
                1,
                10
            )
        )

    table_data = [
        [
            "Date",
            "Work Description",
            "Created By",
            "Created Time"
        ]
    ]

    for item in works:

        created_by = "Unknown"

        if item.created_by:

            created_by = (
                item.created_by.get_full_name()
                or item.created_by.username
            )

        work_text = item.work

        table_data.append(
            [
                item.date.strftime(
                    "%d %b %Y"
                ),
                Paragraph(
                    work_text,
                    styles["Normal"]
                ),
                created_by,
                item.created_at.strftime(
                    "%d %b %Y %I:%M %p"
                )
            ]
        )

    if len(table_data) == 1:

        table_data.append(
            [
                "-",
                "No work records found.",
                "-",
                "-"
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            25 * mm,
            85 * mm,
            35 * mm,
            35 * mm
        ],
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#198754"
                    )
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ]
        )
    )

    elements.append(
        table
    )

    document.build(
        elements
    )

    return response