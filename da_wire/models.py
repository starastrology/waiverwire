from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class MLBTeam(models.Model):
    location = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.location + " " + self.name
    
class Level(models.Model):
    level = models.CharField(max_length=20)
    
    def __str__(self):
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
    colors = models.ManyToManyField(Color)
    logo = models.CharField(max_length=20, default="")
    
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

class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=2, default="", blank=True)
    number = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(99)])
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    mlbaffiliate = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, blank=True)
    is_FA = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    bb_ref = models.CharField(default="", max_length=300)
    
    def __str__(self):
        return self.first_name + " " + self.last_name
    
class Option(models.Model):
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="option_from_level")
    to_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="option_to_level")
    is_rehab_assignment = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    mlbteam = models.ForeignKey(MLBTeam, on_delete=models.CASCADE)
    
class CallUp(models.Model):
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    from_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="callup_from_level")
    to_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="callup_to_level")
    mlbteam = models.ForeignKey(MLBTeam, on_delete=models.CASCADE)
    
class DFA(models.Model):
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_by = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)

class InjuredList(models.Model):
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    length = models.IntegerField(default=10)
    team_for = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)
    
class PersonalLeave(models.Model):
    date = models.DateField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    length = models.IntegerField(default=10)
    team_for = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)
    
class FASignings(models.Model):
    date = models.DateField()
    is_draftpick = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_to = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE)
    
class PlayerTrade(models.Model):
    players = models.ManyToManyField(Player)
    team_from = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, related_name="player_trade_team_from")
    team_to = models.ForeignKey(MLBAffiliate, on_delete=models.CASCADE, related_name="player_trade_team_to")
    
class Trade(models.Model):
    date = models.DateField()
    players = models.ManyToManyField(PlayerTrade)
        
