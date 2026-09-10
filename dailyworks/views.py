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


# =========================================================
# DAILY WORK LIST
# =========================================================

@login_required(login_url="/login/")
def daily_work_list(request):

    works = DailyWork.objects.select_related(
        "created_by"
    ).order_by(
        "-date",
        "created_at"
    )

    return render(
        request,
        "dailyworks/daily_work_list.html",
        {
            "works": works
        }
    )


# =========================================================
# ADD DAILY WORK
# =========================================================

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


# =========================================================
# EDIT DAILY WORK
# =========================================================

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


# =========================================================
# DELETE DAILY WORK
# =========================================================

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


# =========================================================
# DAILY WORK REPORT PAGE
# =========================================================

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
    ).order_by(
        "date",
        "created_at"
    )

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


# =========================================================
# PDF HELPER
# =========================================================

def clean_work_text(text):
    """
    Clean common HTML-like line breaks and extra spaces.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace("<br>", "\n")
    text = text.replace("<br/>", "\n")
    text = text.replace("<br />", "\n")

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def format_work_description(text):
    """
    Converts a work description into readable PDF lines.

    Example:

    Pulling CAT cable 1F zone4. ( CCTV points= 4, Wifi points= 8,
    RFID points= 4 )

    becomes:

    Pulling CAT cable 1F Zone 4
    • CCTV Points – 4
    • WiFi Points – 8
    • RFID Points – 4
    """

    text = clean_work_text(text)

    if not text:
        return []

    lines = []

    # -----------------------------------------------------
    # If the user already entered multiple lines
    # -----------------------------------------------------

    if "\n" in text:

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            lines.append(line)

        return lines

    # -----------------------------------------------------
    # Extract point counts from brackets
    # -----------------------------------------------------

    import re

    point_patterns = [
        (
            r"cctv\s*points?\s*=\s*(\d+)",
            "CCTV Points"
        ),
        (
            r"wifi\s*points?\s*=\s*(\d+)",
            "WiFi Points"
        ),
        (
            r"wi[\s-]*fi\s*points?\s*=\s*(\d+)",
            "WiFi Points"
        ),
        (
            r"rfid\s*points?\s*=\s*(\d+)",
            "RFID Points"
        ),
    ]

    point_values = {}

    for pattern, label in point_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            point_values[label] = match.group(1)

    # -----------------------------------------------------
    # Remove bracket section containing point information
    # -----------------------------------------------------

    main_text = re.sub(
        r"\([^)]*(?:points?|CCTV|WiFi|RFID)[^)]*\)",
        "",
        text,
        flags=re.IGNORECASE
    ).strip()

    # -----------------------------------------------------
    # Remove trailing extra spaces / punctuation
    # -----------------------------------------------------

    main_text = re.sub(
        r"\s+",
        " ",
        main_text
    ).strip()

    # -----------------------------------------------------
    # Capitalize common location words
    # -----------------------------------------------------

    replacements = [
        (
            r"\bzone\s+(\d+)",
            r"Zone \1"
        ),
        (
            r"\bground\s+floor\b",
            "Ground Floor"
        ),
        (
            r"\b1f\b",
            "1F"
        ),
        (
            r"\b2f\b",
            "2F"
        ),
        (
            r"\b3f\b",
            "3F"
        ),
        (
            r"\bcctv\b",
            "CCTV"
        ),
        (
            r"\bwifi\b",
            "WiFi"
        ),
        (
            r"\brfid\b",
            "RFID"
        ),
        (
            r"\bvoice controller\b",
            "Voice Controller"
        ),
        (
            r"\bsunbox\b",
            "Sunbox"
        ),
    ]

    for pattern, replacement in replacements:

        main_text = re.sub(
            pattern,
            replacement,
            main_text,
            flags=re.IGNORECASE
        )

    if main_text:

        # Remove final unnecessary period
        main_text = main_text.rstrip(".")

        lines.append(
            main_text
        )

    # -----------------------------------------------------
    # Add separate point lines
    # -----------------------------------------------------

    point_order = [
        "CCTV Points",
        "WiFi Points",
        "RFID Points",
    ]

    for label in point_order:

        if label in point_values:

            lines.append(
                f"• {label} – {point_values[label]}"
            )

    return lines


# =========================================================
# DAILY WORK PDF
# =========================================================

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
    ).order_by(
        "date",
        "created_at"
    )

    if from_date:

        works = works.filter(
            date__gte=from_date
        )

    if to_date:

        works = works.filter(
            date__lte=to_date
        )

    # -----------------------------------------------------
    # PDF RESPONSE
    # -----------------------------------------------------

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'inline; filename="daily_work_report.pdf"'

    # -----------------------------------------------------
    # PAGE SETTINGS
    # -----------------------------------------------------

    document = SimpleDocTemplate(
        response,
        pagesize=A4,

        rightMargin=14 * mm,
        leftMargin=14 * mm,

        topMargin=14 * mm,
        bottomMargin=14 * mm
    )

    # -----------------------------------------------------
    # COLORS
    # -----------------------------------------------------

    dark_green = colors.HexColor(
        "#146C43"
    )

    light_green = colors.HexColor(
        "#EAF6EF"
    )

    border_green = colors.HexColor(
        "#B7DCC6"
    )

    dark_text = colors.HexColor(
        "#202124"
    )

    grey_text = colors.HexColor(
        "#666666"
    )

    light_grey = colors.HexColor(
        "#F5F6F7"
    )

    white = colors.white

    # -----------------------------------------------------
    # STYLES
    # -----------------------------------------------------

    title_style = ParagraphStyle(
        "ReportTitle",

        fontName="Helvetica-Bold",

        fontSize=18,

        leading=22,

        alignment=TA_CENTER,

        textColor=dark_green,

        spaceAfter=5
    )

    period_style = ParagraphStyle(
        "Period",

        fontName="Helvetica",

        fontSize=9,

        leading=12,

        alignment=TA_CENTER,

        textColor=grey_text,

        spaceAfter=12
    )

    date_style = ParagraphStyle(
        "Date",

        fontName="Helvetica-Bold",

        fontSize=12,

        leading=15,

        textColor=dark_green
    )

    creator_style = ParagraphStyle(
        "Creator",

        fontName="Helvetica",

        fontSize=9,

        leading=12,

        textColor=grey_text
    )

    work_number_style = ParagraphStyle(
        "WorkNumber",

        fontName="Helvetica-Bold",

        fontSize=10,

        leading=13,

        textColor=white,

        alignment=TA_LEFT
    )

    work_description_style = ParagraphStyle(
        "WorkDescription",

        fontName="Helvetica",

        fontSize=10,

        leading=15,

        textColor=dark_text,

        alignment=TA_LEFT
    )

    point_style = ParagraphStyle(
        "Point",

        fontName="Helvetica",

        fontSize=9.5,

        leading=14,

        leftIndent=8,

        textColor=dark_text,

        alignment=TA_LEFT
    )

    no_data_style = ParagraphStyle(
        "NoData",

        fontName="Helvetica",

        fontSize=10,

        leading=14,

        textColor=grey_text,

        alignment=TA_CENTER
    )

    elements = []

    # =====================================================
    # TITLE
    # =====================================================

    elements.append(
        Paragraph(
            "IIT PROJECT - DAILY WORK REPORT",
            title_style
        )
    )

    # -----------------------------------------------------
    # PERIOD
    # -----------------------------------------------------

    if from_date or to_date:

        display_from = (
            from_date
            if from_date
            else "All"
        )

        display_to = (
            to_date
            if to_date
            else "All"
        )

        period_text = (
            f"Period: {display_from} to {display_to}"
        )

    else:

        period_text = "Period: All Records"

    elements.append(
        Paragraph(
            period_text,
            period_style
        )
    )

    # =====================================================
    # NO RECORDS
    # =====================================================

    if not works.exists():

        empty_table = Table(
            [
                [
                    Paragraph(
                        "No work records found.",
                        no_data_style
                    )
                ]
            ],
            colWidths=[
                180 * mm
            ]
        )

        empty_table.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        border_green
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        light_grey
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        20
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        20
                    ),
                ]
            )
        )

        elements.append(
            empty_table
        )

        document.build(
            elements
        )

        return response

    # =====================================================
    # GROUP WORKS BY DATE
    # =====================================================

    grouped = {}

    for item in works:

        date_key = item.date

        if date_key not in grouped:

            grouped[date_key] = []

        grouped[date_key].append(
            item
        )

    # =====================================================
    # BUILD EACH DATE SECTION
    # =====================================================

    for date_index, (work_date, date_works) in enumerate(
        grouped.items()
    ):

        # -------------------------------------------------
        # DATE + CREATOR
        # -------------------------------------------------

        first_item = date_works[0]

        if first_item.created_by:

            created_by = (
                first_item.created_by.get_full_name()
                or first_item.created_by.username
            )

        else:

            created_by = "Unknown"

        date_text = work_date.strftime(
            "%d %b %Y"
        )

        header_data = [
            [
                Paragraph(
                    f"Date: {date_text}",
                    date_style
                ),

                Paragraph(
                    f"Created By: {created_by}",
                    creator_style
                )
            ]
        ]

        header_table = Table(
            header_data,

            colWidths=[
                90 * mm,
                90 * mm
            ]
        )

        header_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        light_green
                    ),

                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        border_green
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
                        10
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                ]
            )
        )

        elements.append(
            header_table
        )

        elements.append(
            Spacer(
                1,
                7
            )
        )

        # -------------------------------------------------
        # WORK ITEMS
        # -------------------------------------------------

        for index, item in enumerate(
            date_works,
            start=1
        ):

            work_lines = format_work_description(
                item.work
            )

            description_elements = []

            for line_number, line in enumerate(
                work_lines
            ):

                safe_line = (
                    line
                    .replace(
                        "&",
                        "&amp;"
                    )
                    .replace(
                        "<",
                        "&lt;"
                    )
                    .replace(
                        ">",
                        "&gt;"
                    )
                )

                if line.startswith("•"):

                    description_elements.append(
                        Paragraph(
                            safe_line,
                            point_style
                        )
                    )

                else:

                    description_elements.append(
                        Paragraph(
                            safe_line,
                            work_description_style
                        )
                    )

            if not description_elements:

                description_elements.append(
                    Paragraph(
                        "No description",
                        work_description_style
                    )
                )

            # ---------------------------------------------
            # WORK NUMBER
            # ---------------------------------------------

            work_number = (
                f"WORK {index:02d}"
            )

            work_number_table = Table(
                [
                    [
                        Paragraph(
                            work_number,
                            work_number_style
                        )
                    ]
                ],

                colWidths=[
                    180 * mm
                ]
            )

            work_number_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            dark_green
                        ),

                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            10
                        ),

                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            10
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

            # ---------------------------------------------
            # DESCRIPTION BOX
            # ---------------------------------------------

            description_table = Table(
                [
                    [
                        description_elements
                    ]
                ],

                colWidths=[
                    180 * mm
                ]
            )

            description_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            white
                        ),

                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.7,
                            border_green
                        ),

                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            10
                        ),

                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            10
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            9
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            9
                        ),

                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP"
                        ),
                    ]
                )
            )

            # ---------------------------------------------
            # KEEP WORK NUMBER + DESCRIPTION TOGETHER
            # ---------------------------------------------

            elements.append(
                KeepTogether(
                    [
                        work_number_table,
                        description_table,
                    ]
                )
            )

            elements.append(
                Spacer(
                    1,
                    8
                )
            )

        # -------------------------------------------------
        # SPACE BETWEEN DATES
        # -------------------------------------------------

        if date_index < len(grouped):

            elements.append(
                Spacer(
                    1,
                    6
                )
            )

    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(
        elements
    )

    return response