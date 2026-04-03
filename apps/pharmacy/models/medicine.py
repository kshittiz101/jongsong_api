from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from common.image_validators import validate_image_file_size, validate_image_file_integrity

from .category import Category
from .supplier import Supplier

_IMAGE_VALIDATORS = [
    FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
    validate_image_file_size,
    validate_image_file_integrity,
]


class Medicine(models.Model):
    """
    Medicine model stores all medicine details including stock/batch information.
    """

    image = models.ImageField(
        upload_to="medicine_images/", blank=True, null=True, validators=_IMAGE_VALIDATORS
    )
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    brand_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    strength = models.CharField(max_length=50, help_text="e.g. 500mg")
    requires_prescription = models.BooleanField(default=False)
    reorder_level = models.PositiveIntegerField(
        default=10,
        help_text="Alert when stock falls below this level",
    )

    # Batch / Stock fields
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    quantity_received = models.PositiveIntegerField(default=0)
    quantity_remaining = models.PositiveIntegerField(default=0)

    # price fields
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price_after_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)

    # Foreign Keys
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="medicines"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicines",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.strength})"

    def save(self, *args, **kwargs):
        # Treat `discount` as a percentage (e.g. 10 => 10% off).
        base_price = self.purchase_price or Decimal("0")
        discount_pct = self.discount or Decimal("0")

        if discount_pct < 0:
            discount_pct = Decimal("0")
        if discount_pct > 100:
            discount_pct = Decimal("100")

        if discount_pct == 0:
            discounted = base_price
        else:
            discounted = base_price * (Decimal("1") - (discount_pct / Decimal("100")))
        if discounted < 0:
            discounted = Decimal("0")

        self.selling_price_after_discount = discounted.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        super().save(*args, **kwargs)

    @property
    def total_stock(self):
        """Returns the current quantity remaining."""
        return self.quantity_remaining

    @property
    def is_low_stock(self):
        return self.quantity_remaining <= self.reorder_level

    @property
    def is_expired(self):
        if self.expiry_date is None:
            return False
        return self.expiry_date <= timezone.now().date()

    @property
    def days_to_expiry(self):
        if self.expiry_date is None:
            return None
        delta = self.expiry_date - timezone.now().date()
        return delta.days

    @property
    def is_expiring_soon(self):
        """Returns True if medicine expires within 90 days."""
        days = self.days_to_expiry
        if days is None:
            return False
        return 0 < days <= 90
