# Generated by Django 3.2.6 on 2021-10-08 10:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('da_wire', '0003_auto_20211008_0934'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_rehab_assignment', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('from_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='option_proposal_from_level', to='da_wire.level')),
                ('mlbteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbteam')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('to_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='option_proposal_to_level', to='da_wire.level')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CallUpProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('from_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='callup_proposal_from_level', to='da_wire.level')),
                ('mlbteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbteam')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('to_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='callup_proposal_to_level', to='da_wire.level')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
