# Generated by Django 3.2.6 on 2021-08-24 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0003_alter_mlbaffiliate_colors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='color',
            name='pkey',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]