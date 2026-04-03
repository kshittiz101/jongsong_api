from django.db import models


class Designation(models.Model):
    """
    This model is used to store the designation information.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


def default_other_designation_pk():
    """DB default for profiles; matches the seeded \"Other\" designation (see migration)."""
    return Designation.objects.filter(name="Other").values_list("pk", flat=True).first()
