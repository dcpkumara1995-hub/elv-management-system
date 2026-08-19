from django.contrib import admin
from .models import StockItem, StockMovement


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "quantity",
        "unit",
        "minimum_stock",
        "updated_at",
    )
    search_fields = ("name", "category")
    list_filter = ("category",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "movement_type",
        "quantity",
        "note",
        "created_at",
    )
    search_fields = ("item__name", "note")
    list_filter = ("movement_type", "created_at")