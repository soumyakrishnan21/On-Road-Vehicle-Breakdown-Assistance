# Generated by Django 5.0.6 on 2024-08-22 16:08

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Webapp", "0024_remove_cart_order_id_order_cartid_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="cartid",
        ),
        migrations.AddField(
            model_name="cart",
            name="order_id",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_items",
                to="Webapp.order",
            ),
        ),
        migrations.AlterField(
            model_name="booking",
            name="date_booked",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 8, 22, 21, 38, 22, 405918)
            ),
        ),
    ]
