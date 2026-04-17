from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("homecare", "0002_alter_medication_frequency"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PatientCareAssignment",
        ),
    ]
