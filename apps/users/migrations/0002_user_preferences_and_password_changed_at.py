from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="password_changed_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Password changed at",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="preferences",
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name="Preferences",
            ),
        ),
    ]
