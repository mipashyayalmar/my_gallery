# Generated by Django 4.2.2 on 2024-11-01 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pgsApp", "0007_alter_notification_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[("all", "All Users"), ("user", "Specific User")],
                default="user",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
