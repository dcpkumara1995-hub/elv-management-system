from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import StockItem, StockMovement


@login_required(login_url="/login/")
def stock_home(request):

    return render(
        request,
        "stock/stock_home.html"
    )


@login_required(login_url="/login/")
def current_stock(request):

    items = StockItem.objects.all().order_by("name")

    return render(
        request,
        "stock/current_stock.html",
        {"items": items}
    )


@login_required(login_url="/login/")
def stock_update(request):

    items = StockItem.objects.all().order_by("name")

    if request.method == "POST":

        item_id = request.POST.get("item")
        movement_type = request.POST.get("movement_type")
        quantity_text = request.POST.get("quantity")
        note = request.POST.get("note", "")

        try:

            item = StockItem.objects.get(id=item_id)

            quantity = Decimal(quantity_text)

            if quantity <= 0:
                raise ValueError(
                    "Quantity must be greater than 0."
                )

            StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=quantity,
                note=note
            )

            messages.success(
                request,
                f"{item.name} stock updated successfully."
            )

        except (InvalidOperation, ValueError) as e:

            messages.error(
                request,
                str(e)
            )

        except Exception as e:

            messages.error(
                request,
                str(e)
            )

        return redirect("stock_update")

    return render(
        request,
        "stock/stock_update.html",
        {"items": items}
    )


@login_required(login_url="/login/")
def add_item(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        category = request.POST.get(
            "category",
            ""
        ).strip()

        unit = request.POST.get(
            "unit",
            "Nos"
        ).strip()

        quantity_text = request.POST.get(
            "quantity",
            "0"
        ).strip()

        minimum_stock_text = request.POST.get(
            "minimum_stock",
            "0"
        ).strip()

        if not name:

            messages.error(
                request,
                "Item name is required."
            )

            return redirect("add_item")

        if not unit:

            unit = "Nos"

        try:

            quantity = Decimal(
                quantity_text
            )

            minimum_stock = Decimal(
                minimum_stock_text
            )

            if quantity < 0:

                raise ValueError(
                    "Opening quantity cannot be negative."
                )

            if minimum_stock < 0:

                raise ValueError(
                    "Minimum stock cannot be negative."
                )

        except (InvalidOperation, ValueError):

            messages.error(
                request,
                "Please enter valid quantities."
            )

            return redirect("add_item")

        if StockItem.objects.filter(
            name__iexact=name
        ).exists():

            messages.error(
                request,
                "This item already exists."
            )

            return redirect("add_item")

        StockItem.objects.create(
            name=name,
            category=category,
            quantity=quantity,
            unit=unit,
            minimum_stock=minimum_stock
        )

        messages.success(
            request,
            f"{name} added successfully."
        )

        return redirect("stock_update")

    return render(
        request,
        "stock/add_item.html"
    )


@login_required(login_url="/login/")
def delete_item(request, item_id):

    # Only Super Users can delete stock items

    if not request.user.is_superuser:

        messages.error(
            request,
            "You do not have permission to delete stock items."
        )

        return redirect("current_stock")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid delete request."
        )

        return redirect("current_stock")

    try:

        item = StockItem.objects.get(
            id=item_id
        )

        item_name = item.name

        item.delete()

        messages.success(
            request,
            f"{item_name} deleted successfully."
        )

    except StockItem.DoesNotExist:

        messages.error(
            request,
            "Stock item not found."
        )

    return redirect("current_stock")


@login_required(login_url="/login/")
def reports(request):

    movements = StockMovement.objects.select_related(
        "item"
    ).all().order_by("-created_at")

    return render(
        request,
        "stock/reports.html",
        {"movements": movements}
    )