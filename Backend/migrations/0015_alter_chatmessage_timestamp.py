# Generated by Django 5.0.6 on 2024-08-21 14:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Backend", "0014_alter_chatmessage_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="timestamp",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 8, 21, 14, 38, 15, 95252, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
