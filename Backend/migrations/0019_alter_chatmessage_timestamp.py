# Generated by Django 5.0.6 on 2024-08-22 16:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Backend", "0018_alter_chatmessage_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="timestamp",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 8, 22, 16, 8, 22, 392035, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
