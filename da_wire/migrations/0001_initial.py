# Generated by Django 3.2.6 on 2022-01-17 16:56

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BatterStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avg', models.DecimalField(decimal_places=3, max_digits=4)),
                ('OBP', models.DecimalField(decimal_places=3, max_digits=4)),
                ('OPS', models.DecimalField(decimal_places=3, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('pkey', models.IntegerField(primary_key=True, serialize=False)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('text', models.TextField(validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(2000)])),
                ('reply_to', models.IntegerField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=20)),
                ('rookie_level', models.IntegerField(blank=True, default=0)),
                ('value', models.IntegerField(blank=True, default=1)),
            ],
        ),
        migrations.CreateModel(
            name='MLBAffiliate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('logo', models.CharField(default='', max_length=20)),
                ('abbreviation', models.CharField(default='', max_length=10)),
                ('roster_url', models.CharField(blank=True, max_length=50)),
                ('colors', models.ManyToManyField(blank=True, to='da_wire.Color')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.level')),
            ],
        ),
        migrations.CreateModel(
            name='MLBTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('is_NL', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='PitcherStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ERA', models.DecimalField(decimal_places=2, max_digits=6)),
                ('SO', models.IntegerField()),
                ('WHIP', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_initial', models.CharField(blank=True, default='', max_length=2)),
                ('number', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99)])),
                ('is_FA', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('bb_ref', models.CharField(default='', max_length=300)),
                ('first_name_unaccented', models.CharField(max_length=50)),
                ('last_name_unaccented', models.CharField(max_length=50)),
                ('picture', models.CharField(blank=True, default=None, max_length=1000)),
                ('mlbaffiliate', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbaffiliate')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerTrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('players', models.ManyToManyField(to='da_wire.Player')),
                ('team_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_trade_team_from', to='da_wire.mlbaffiliate')),
                ('team_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_trade_team_to', to='da_wire.mlbaffiliate')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerTradeProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('players', models.ManyToManyField(to='da_wire.Player')),
                ('team_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_trade_proposal_team_from', to='da_wire.mlbaffiliate')),
                ('team_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_trade_proposal_team_to', to='da_wire.mlbaffiliate')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('years', models.IntegerField(default=1)),
                ('money', models.IntegerField(default=30000)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('tid', models.AutoField(primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='WaiverClaim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('team_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='waiver_claim_team_from', to='da_wire.mlbaffiliate')),
                ('team_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='waiver_claim_team_to', to='da_wire.mlbaffiliate')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_up', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TradeProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('players', models.ManyToManyField(to='da_wire.PlayerTradeProposal')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('players', models.ManyToManyField(to='da_wire.PlayerTrade')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_mlb', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('batter_stats', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='da_wire.batterstats')),
                ('pitcher_stats', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='da_wire.pitcherstats')),
            ],
        ),
        migrations.CreateModel(
            name='ReplyNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.comment')),
            ],
        ),
        migrations.CreateModel(
            name='ProUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.position'),
        ),
        migrations.AddField(
            model_name='player',
            name='salary',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='da_wire.salary'),
        ),
        migrations.AddField(
            model_name='player',
            name='stats',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='da_wire.stats'),
        ),
        migrations.AddField(
            model_name='player',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
        ),
        migrations.CreateModel(
            name='PersonalLeave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('length', models.IntegerField(default=10)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('team_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbaffiliate')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
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
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_rehab_assignment', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('from_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='option_from_level', to='da_wire.level')),
                ('mlbteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbteam')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('to_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='option_to_level', to='da_wire.level')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
        migrations.AddField(
            model_name='mlbaffiliate',
            name='mlbteam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbteam'),
        ),
        migrations.CreateModel(
            name='InjuredList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('length', models.IntegerField(default=10)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('team_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbaffiliate')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='FASigningsProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_draftpick', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('salary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.salary')),
                ('team_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbaffiliate')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FASignings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_draftpick', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('team_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbaffiliate')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='DFA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('team_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbaffiliate')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_up', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='transaction',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
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
        migrations.CreateModel(
            name='CallUp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('from_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='callup_from_level', to='da_wire.level')),
                ('mlbteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.mlbteam')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.player')),
                ('to_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='callup_to_level', to='da_wire.level')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='da_wire.transaction')),
            ],
        ),
        migrations.AddConstraint(
            model_name='transactionvote',
            constraint=models.UniqueConstraint(fields=('user', 'transaction'), name='unique_user_transaction'),
        ),
        migrations.AddConstraint(
            model_name='commentvote',
            constraint=models.UniqueConstraint(fields=('user', 'comment'), name='unique_user_comment'),
        ),
    ]
