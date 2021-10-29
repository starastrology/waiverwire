from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, \
    MaxLengthValidator, MinLengthValidator
from django.contrib.auth.models import User

class ProUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #is_pro = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])

class MLBTeam(models.Model):
    location = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    is_NL = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])

    def __str__(self):
        return self.location + " " + self.name
    
class Level(models.Model):
    level = models.CharField(max_length=20)
    rookie_level = models.IntegerField(default=0, blank=True)
    value = models.IntegerField(default=1, blank=True)

    def __str__(self):
        if self.rookie_level:
            return self.level + str(self.rookie_level)
        else:
            return self.level

class Color(models.Model):
    pkey = models.IntegerField(primary_key=True)
    color = models.CharField(max_length=10)
    
    def __str__(self):
        return self.color
        
class MLBAffiliate(models.Model):
    location = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    mlbteam = models.ForeignKey(MLBTeam, on_delete=models.CASCADE)
    colors = models.ManyToManyField(Color, blank=True)
    logo = models.CharField(max_length=20, default="")
    abbreviation = models.CharField(max_length=10, default="")
    roster_url = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.location + " " + self.name

class Salary(models.Model):
    years = models.IntegerField(default=1)
    money = models.IntegerField(default=30000)
    
    def __str__(self):
        return str(self.years) + " years : $" + str(self.money)

class Position(models.Model):
    position = models.CharField(max_length=20)
    
    def __str__(self):
        return self.position
    
class Transaction(models.Model):
    tid = models.AutoField(primary_key=True)

class PitcherStats(models.Model):
    ERA = models.DecimalField(max_digits=6, decimal_places=2)
    SO = models.IntegerField()
    WHIP = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return str(self.ERA) + "/" + str(self.SO) + "/" + str(self.WHIP)

class BatterStats(models.Model):
    avg = models.DecimalField(max_digits=4, decimal_places=3)
    OBP = models.DecimalField(max_digits=4, decimal_places=3)
    OPS = models.DecimalField(max_digits=4, decimal_places=3)
    
    def __str__(self):
        return str(self.avg) + "/" + str(self.OBP) + "/" + str(self.OPS)

class Stats(models.Model):
    is_mlb = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    pitcher_stats = models.ForeignKey(PitcherStats, on_delete=models.CASCADE, default=None, null=True, blank=True)
    batter_stats = models.ForeignKey(BatterStats, on_delete=models.CASCADE, default=None, null=True, blank=True) 

    """
    def __str__(self):
        if self.pitcher_stats:
            return self.pitcher_stats
        else:
            return self.batter_stats
    """

class Player(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=2, default="", blank=True)
    number = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(99)])
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    mlbaffiliate = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, blank=True)
    is_FA = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    bb_ref = models.CharField(default="", max_length=300)
    first_name_unaccented = models.CharField(max_length=50)
    last_name_unaccented = models.CharField(max_length=50)
    picture = models.CharField(max_length=1000, default=None, blank=True)
    stats = models.ForeignKey(Stats, on_delete=models.CASCADE, default=None, null=True, blank=True)


    def __str__(self):
        return self.first_name + " " + self.middle_initial + " " + self.last_name

class Option(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="option_from_level")
    to_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="option_to_level")
    is_rehab_assignment = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    mlbteam = models.ForeignKey(MLBTeam, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date) + " " + self.player.first_name + " " + self.player.last_name

class OptionProposal(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="option_proposal_from_level")
    to_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="option_proposal_to_level")
    is_rehab_assignment = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    mlbteam = models.ForeignKey(MLBTeam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.date) + " " + self.player.first_name + " " + self.player.last_name




class CallUp(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="callup_from_level")
    to_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="callup_to_level")
    mlbteam = models.ForeignKey(MLBTeam, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date) + " " + self.player.first_name + " " + self.player.last_name

class CallUpProposal(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="callup_proposal_from_level")
    to_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="callup_proposal_to_level")
    mlbteam = models.ForeignKey(MLBTeam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.date) + " " + self.player.first_name + " " + self.player.last_name

class DFA(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_by = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date) + " " + self.player.first_name + " " + self.player.last_name

class InjuredList(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    length = models.IntegerField(default=10)
    team_for = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.date) + " " + self.player.first_name + " " + self.player.last_name

class PersonalLeave(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    length = models.IntegerField(default=10)
    team_for = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)
    
class FASignings(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    is_draftpick = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_to = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)

    def __str__(self):
        return self.player.first_name + " " + self.player.last_name + " to " + self.team_to.name

class FASigningsProposal(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    is_draftpick = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_to = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.player.first_name + " " + self.player.last_name + " to " + self.team_to.name



class PlayerTrade(models.Model):
    players = models.ManyToManyField(Player)
    team_from = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, related_name="player_trade_team_from")
    team_to = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, related_name="player_trade_team_to")
    
class PlayerTradeProposal(models.Model):
    players = models.ManyToManyField(Player)
    team_from = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, related_name="player_trade_proposal_team_from")
    team_to = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, related_name="player_trade_proposal_team_to")

class Trade(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    players = models.ManyToManyField(PlayerTrade)
   
    def __str__(self):
        return str(self.date) + " - involving " + self.players.all()[0].team_from.name

class TradeProposal(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField()
    players = models.ManyToManyField(PlayerTradeProposal)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.date) + " - involving " + self.players.all()[0].team_from.name



class TransactionVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_up = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(1)])
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'transaction'], name='unique_user_transaction'),
        ]
   
class Comment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, default=None)
    datetime = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    text = models.TextField(validators=[MinLengthValidator(1), MaxLengthValidator(2000)])
    
class CommentVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_up = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(1)])
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_user_comment'),
        ]
        
