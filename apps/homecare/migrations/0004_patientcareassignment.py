import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("homecare", "0003_remove_patientcareassignment"),
    ]

    operations = [
        migrations.CreateModel(
            name="PatientCareAssignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "doctor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="doctor_care_assignments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "nurse",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="nurse_care_assignments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="care_assignments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-assigned_at", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="patientcareassignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_active=True),
                fields=("patient",),
                name="homecare_unique_active_care_assignment_v2",
            ),
        ),
    ]
