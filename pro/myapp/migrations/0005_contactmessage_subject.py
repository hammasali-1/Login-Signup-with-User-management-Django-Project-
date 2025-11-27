from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0004_customers_theme"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactmessage",
            name="subject",
            field=models.CharField(max_length=120, null=True, blank=True),
        ),
    ]

