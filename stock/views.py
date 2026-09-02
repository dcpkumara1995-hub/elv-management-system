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
def reports(request):

    movements = StockMovement.objects.select_related(
        "item"
    ).all().order_by("-created_at")

    return render(
        request,
        "stock/reports.html",
        {"movements": movements}
    )
