# Generated by Django 5.0.6 on 2024-08-15 18:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Webapp", "0011_delete_messagedb_delete_messages_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="date_booked",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 8, 15, 23, 41, 30, 765709)
            ),
        ),
    ]
