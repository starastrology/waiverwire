# Generated by Django 3.2.6 on 2021-10-29 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0013_auto_20211029_0052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batterstats',
            name='OBP',
            field=models.DecimalField(decimal_places=3, max_digits=4),
        ),
        migrations.AlterField(
            model_name='batterstats',
            name='avg',
            field=models.DecimalField(decimal_places=3, max_digits=4),
        ),
    ]