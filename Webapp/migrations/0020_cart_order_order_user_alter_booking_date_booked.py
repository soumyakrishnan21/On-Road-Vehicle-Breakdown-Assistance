# Generated by Django 5.0.6 on 2024-08-21 14:21

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Webapp", "0019_alter_booking_date_booked"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="order",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_items",
                to="Webapp.order",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="Webapp.userdatas",
            ),
        ),
        migrations.AlterField(
            model_name="booking",
            name="date_booked",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 8, 21, 19, 51, 28, 250730)
            ),
        ),
    ]
