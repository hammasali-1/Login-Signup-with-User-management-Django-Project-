from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_siteinfo_alter_customers_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customers",
            name="theme",
            field=models.CharField(
                max_length=10,
                choices=(("light","Light"),("dark","Dark")),
                default="light",
            ),
        ),
    ]

