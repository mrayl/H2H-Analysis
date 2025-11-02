from django.db import models

# Create your models here.

class Player(models.Model):
    # ID from stats.nba.com - Will be the Primary Key
    api_id = models.IntegerField(unique=True, primary_key=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Current Team Info for the Player
    team_api_id = models.IntegerField(null=True, blank=True)
    team_name = models.CharField(max_length=100, default='', blank=True)
    team_abbreviation = models.CharField(max_length=10, default='', blank=True)
    
    def __str__(self):
        if self.team_abbreviation:
            return f"{self.first_name} {self.last_name} ({self.team_abbreviation})"
        return f"{self.first_name} {self.last_name}"