# Generated by Django 3.2.6 on 2021-10-29 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0010_alter_player_stats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='stats',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='da_wire.stats'),
        ),
    ]
