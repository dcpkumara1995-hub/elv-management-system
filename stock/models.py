from django.db import models
from django.core.exceptions import ValidationError


class StockItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, default="Nos")
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    ]

    item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name="movements"
    )
    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_TYPES
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0.")

            if self.movement_type == "OUT":
                if self.item.quantity < self.quantity:
                    raise ValidationError("Not enough stock available.")

                self.item.quantity -= self.quantity

            elif self.movement_type == "IN":
                self.item.quantity += self.quantity

            self.item.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.movement_type} - {self.quantity}"