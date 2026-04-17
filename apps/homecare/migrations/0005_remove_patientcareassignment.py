from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("homecare", "0004_patientcareassignment"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PatientCareAssignment",
        ),
    ]
