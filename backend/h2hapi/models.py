from django.db import models

# Create your models here.

class Player(models.Model):
    # ID from balldontlie API - Will be the Primary Key
    api_id = models.IntegerField(unique=True, primary_key=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharFIeld(max_length=100)
    
    # Current Team Info for the Player
    team_api_id = models.IntegerField()
    team_name = models.CharField(max_lenth=100, default='')
    team_abbreviation = models.CharFIeld(max_lenth=10, default='')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.team_abbreviation})"