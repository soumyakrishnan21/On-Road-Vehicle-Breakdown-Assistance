# Generated by Django 5.0.6 on 2024-08-21 14:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Backend", "0015_alter_chatmessage_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="timestamp",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 8, 21, 14, 58, 43, 439955, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
