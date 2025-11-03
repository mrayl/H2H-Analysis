from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Player
from .serializers import PlayerSerializer
import time
import pandas as pd
import json
import requests

# Create your views here.
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import playergamelog

CURRENT_SEASON = "2024-2025"

class PlayerListView(ListAPIView):
    # Lists all active players for the search box
    
    queryset = Player.objects.all().order_by('last_name') # Gets all players from the database
    serializer_class = PlayerSerializer

class ComparePlayersView(APIView):
    def get(self, request, *args, **kwargs):
        # Get Player Ids
        try:
            player_a_id = int(request.query_params.get('player_a_id'))
            player_b_id = int(request.query_params.get('player_b_id'))
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid player IDs. Please provide two valid integers."},
                status=400
            )
            
        season = request.query_params.get('season', CURRENT_SEASON)
        
        print(f"Comparing {player_a_id} vs {player_b_id} for {season}")
        
        try:
            
           # Get Season Stats
            print(f"Fetching season stats for Player A ({player_a_id})...")
            season_stats_a = self.get_season_stats(player_a_id, season)
            
            print(f"Fetching season stats for Player B ({player_b_id})...")
            season_stats_b = self.get_season_stats(player_b_id, season)

            # Get player details
            details_a = self.get_player_details(player_a_id)
            details_b = self.get_player_details(player_b_id)
        
            # Build Response
            response_data = {
                "player_a_id": player_a_id,
                "player_b_id": player_b_id,
                "season": season,
                "player_a_details": {
                    **details_a, 
                    "team_id": season_stats_a.get("team_id"),
                    "team_abbreviation": season_stats_a.get("team_abbreviation"),
                },
                "player_b_details": {
                    **details_b,
                    "team_id": season_stats_b.get("team_id"),
                    "team_abbreviation": season_stats_b.get("team_abbreviation"),
                },
                "season_stats": {
                    "player_a": season_stats_a,
                    "player_b": season_stats_b,
                }, 
                "h2h_stats": {} # We will do H2H next
            }
            
            # Update Dictionary for Player A
            update_data_a = {}
            if season_stats_a.get("team_id"):
                update_data_a['team_api_id'] = season_stats_a.get("team_id")
            if season_stats_a.get("team_abbreviation"):
                update_data_a['team_abbreviation'] = season_stats_a.get("team_abbreviation")
            # Only update if there's new data
            if update_data_a:
                Player.objects.filter(api_id=player_a_id).update(**update_data_a)
             
            # Update Dictionary for Player B   
            update_data_b = {}
            if season_stats_b.get("team_id"):
                update_data_b['team_api_id'] = season_stats_b.get("team_id")
            if season_stats_b.get("team_abbreviation"):
                update_data_b['team_abbreviation'] = season_stats_b.get("team_abbreviation")

            if update_data_b:
                Player.objects.filter(api_id=player_b_id).update(**update_data_b)

            # H2H Logic will go here
            
            print("All data fetched successfully")
            return Response(response_data, status=200)
        except Exception as e:
            # general error handler
            print(f"Error in 'get' method: {e}")
            return Response(
                {"error": f"An error occurred while fetching data: {str(e)}"},
                status=500
            )
            
    def get_player_details(self, player_id):
        # Helper Function - gets players' names and teams
        try:
            player = Player.objects.get(api_id=player_id)
            return {
                "first_name": player.first_name,
                "last_name": player.last_name,
            }
        except Player.DoesNotExist:
            return {"error": "Player not found in local DB"}
    
    def get_season_stats(self, player_id, season):
        
        print(f"Fetching LeagueDashPlayerStats for {player_id} in {season}...")
        time.sleep(1.1) 
        
        try:
            # API Call
            stats_endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                Player_ID_Nullable=player_id,
                season_type_all_star="Regular Season"
            )
            
            stats_dict = stats_endpoint.get_dict()

            if 'resultSets' not in stats_dict or not stats_dict['resultSets']:
                raise Exception("API Response missing 'resultSets'")

            data = stats_dict['resultSets'][0]
            headers = data['headers']
            rows = data['rowSet']
            
            if not rows:
                # Player had no stats for this season (e.g., injured)
                return {"game_count": 0}

            stats_df = pd.DataFrame(rows, columns=headers)
            total_stats = stats_df.iloc[0]

            # Calculate Advanced Stats
            try:
                efg_pct = (total_stats['FGM'] + 0.5 * total_stats['FG3M']) / total_stats['FGA']
            except ZeroDivisionError:
                efg_pct = 0
                
            try:
                tsp_pct = total_stats['PTS'] / (2 * (total_stats['FGA'] + 0.44 * total_stats['FTA']))
            except ZeroDivisionError:
                tsp_pct = 0
            
            game_count = total_stats['GP'] # Get Game Count

            # Calculate Averages
            avg_cols = [
                'MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 
                'FTA', 'OREB', 'DREB', 'REB', 'AST', 'STL', 
                'BLK', 'TOV', 'PF', 'PTS'
            ]
            avg_stats = {}
            for col in avg_cols:
                # Ensure data is numeric before dividing
                total = pd.to_numeric(total_stats[col])
                avg = total / game_count
                avg_stats[col] = round(avg, 1)

            # Return the data
            return {
                "game_count": int(game_count),
                "team_id": int(total_stats['TEAM_ID']),
                "team_abbreviation": total_stats['TEAM_ABBREVIATION'],
                "avg_stats": avg_stats,
                "advanced_stats": {
                    "efg_pct": round(efg_pct, 3),
                    "tsp_pct": round(tsp_pct, 3),
                },
                "total_stats": total_stats.to_dict()
            }

        except Exception as e:
            print(f"Error in get_season_stats for {player_id}: {e}")
            # This could be a 'resultSet' error if the player played for
            # no teams that season.
            return {"game_count": 0, "error": str(e)}