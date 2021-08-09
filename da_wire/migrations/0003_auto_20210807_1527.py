# Generated by Django 3.2.5 on 2021-08-07 19:27

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('da_wire', '0002_mlbaffiliate_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('tid', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_up', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
            ],
        ),
        migrations.AddField(
            model_name='callup',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dfa',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fasignings',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='injuredlist',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='option',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='personalleave',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trade',
            name='transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
            preserve_default=False,
        ),
    ]