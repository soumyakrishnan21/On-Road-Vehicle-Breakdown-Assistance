# Generated by Django 5.0.6 on 2024-08-15 17:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Webapp", "0005_rename_chatmessages_chatmessage_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="date_booked",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 8, 15, 23, 9, 26, 347359)
            ),
        ),
        # migrations.AlterField(
        #     model_name="messages",
        #     name="date",
        #     field=models.DateTimeField(
        #         blank=True, default=datetime.datetime(2024, 8, 15, 23, 9, 26, 349354)
        #     ),
        # ),
    ]
