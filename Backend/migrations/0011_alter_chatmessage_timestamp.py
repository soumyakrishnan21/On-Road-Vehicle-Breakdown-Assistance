# Generated by Django 5.0.6 on 2024-08-17 14:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Backend", "0010_alter_chatmessage_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="timestamp",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
