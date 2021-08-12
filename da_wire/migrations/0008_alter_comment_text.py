# Generated by Django 3.2.5 on 2021-08-12 15:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0007_alter_comment_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(2000)]),
        ),
    ]
