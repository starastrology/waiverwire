# Generated by Django 3.2.9 on 2021-11-12 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0016_transactionvote_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='reply_to',
            field=models.IntegerField(default=None),
        ),
    ]
