# Generated by Django 5.0.6 on 2024-08-15 18:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Webapp", "0012_alter_booking_date_booked"),
    ]

    operations = [
        # migrations.DeleteModel(
        #     name="Chatmessage",
        # ),
        migrations.AlterField(
            model_name="booking",
            name="date_booked",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 8, 15, 23, 43, 25, 978932)
            ),
        ),
    ]
