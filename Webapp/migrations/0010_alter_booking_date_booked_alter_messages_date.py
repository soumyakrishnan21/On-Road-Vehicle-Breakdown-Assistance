# Generated by Django 5.0.6 on 2024-08-15 17:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Webapp", "0009_alter_booking_date_booked_alter_messages_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="date_booked",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 8, 15, 23, 19, 49, 108400)
            ),
        ),
        # migrations.AlterField(
        #     model_name="messages",
        #     name="date",
        #     field=models.DateTimeField(
        #         blank=True, default=datetime.datetime(2024, 8, 15, 23, 19, 49, 110563)
        #     ),
        # ),
    ]
