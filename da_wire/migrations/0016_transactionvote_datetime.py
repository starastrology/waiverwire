# Generated by Django 3.2.9 on 2021-11-11 05:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0015_waiverclaim'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionvote',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]