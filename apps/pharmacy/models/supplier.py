from django.db import models


class Supplier(models.Model):
    """
    This model is used to store the supplier information.
    """

    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.name}"

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
