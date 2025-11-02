from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Player
from .serializers import PlayerSerializer

# Create your views here.
class PlayerListView(ListAPIView):
    # Lists all active players for the search box
    
    queryset = Player.objects.all().order_by('last_name') # Gets all players from the database
    serializer_class = PlayerSerializer