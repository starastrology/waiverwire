# Generated by Django 3.2.6 on 2021-10-27 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0006_fasigningsproposal'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='picture',
            field=models.CharField(default=None, max_length=1000),
        ),
    ]
