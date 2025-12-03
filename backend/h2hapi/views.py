from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import Player
from .serializers import PlayerSerializer, ComparisonRequestSerializer
import time
import pandas as pd
import json
import requests

# Create your views here.
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import playercareerstats

CURRENT_SEASON = "2025-26"

class PlayerListView(ListAPIView):
    # Lists all active players for the search box
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    queryset = Player.objects.all().order_by('last_name') # Gets all players from the database
    serializer_class = PlayerSerializer

class ComparePlayersView(APIView):
    
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        
        serializer = ComparisonRequestSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)
        
        validated_data = serializer.validated_data
        player_a_id = validated_data['player_a_id']
        player_b_id = validated_data['player_b_id']
        raw_season = validated_data['season']
        
        
        # Format the season
        if len(raw_season) == 9 and raw_season[4] =='-':
            formatted_season = raw_season[:5] + raw_season[-2:] # Format the season from 2024-2025 to 2024-25
        else:
            formatted_season = raw_season
        
        print(f"Comparing {player_a_id} vs {player_b_id} for {formatted_season}")
        
        try:
            
           # Get Season Stats
            print(f"Fetching season stats for Player A ({player_a_id})...")
            season_stats_a = self.get_season_stats(player_a_id, formatted_season)
            
            print(f"Fetching season stats for Player B ({player_b_id})...")
            season_stats_b = self.get_season_stats(player_b_id, formatted_season)
            
            # Get Gamelogs
            print(f"Fetching full gamelog for Player A ({player_a_id})...")
            gamelog_a = self.get_player_gamelog(player_a_id, formatted_season)
            
            print(f"Fetching full gamelog for Player B ({player_b_id})...")
            gamelog_b = self.get_player_gamelog(player_b_id, formatted_season)
            
            # Compute H2H Stats
            print("Computing H2H stats...")
            h2h_stats = self.compute_h2h_stats(gamelog_a, gamelog_b)

            # Get player details
            details_a = self.get_player_details(player_a_id)
            details_b = self.get_player_details(player_b_id)
        
            # Build Response
            response_data = {
                "player_a_id": player_a_id,
                "player_b_id": player_b_id,
                "season": formatted_season,
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
                "h2h_stats": h2h_stats # We will do H2H next
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
        # gets players' names and teams
        try:
            player = Player.objects.get(api_id=player_id)
            return {
                "first_name": player.first_name,
                "last_name": player.last_name,
            }
        except Player.DoesNotExist:
            return {"error": "Player not found in local DB"}
    
    def get_season_stats(self, player_id, season):
        
        print(f"Fetching Fetching PlayerCareerStats for {player_id} in {season}...")
        time.sleep(1.1) 
        
        try:
            # API Call
            career_stats_endpoint = playercareerstats.PlayerCareerStats(
                player_id=player_id,
            )
            
            stats_df = career_stats_endpoint.get_data_frames()[0]
            
            if stats_df.empty:
                return {"game_count": 0, "error": "No career stats found for player."}

            season_stats_series = stats_df[stats_df['SEASON_ID'] == season]
            
            if season_stats_series.empty:
                # Player had no stats for this season (e.g., injured, not in league)
                return {"game_count": 0, "error": "No stats found for this season."}

            # Get the first (and only) row for that season
            total_stats = season_stats_series.iloc[0]

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
                if game_count == 0:
                    avg = 0
                else:
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
            # This could be a 'resultSet' error
            return {"game_count": 0, "error": str(e)}
        
    def get_player_gamelog(self, player_id, season):
        # Fetches full gamelog for a player in a given season
        print(f"Fetching GameLog for {player_id} in {season}...")
        time.sleep(1.1)
        
        try:
            gamelog_endpoint = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season,
                season_type_all_star="Regular Season"
            )
            
            return gamelog_endpoint.get_data_frames()[0]
        except Exception as e:
            print(f"Error fetching gamelog for {player_id}: {e}")
            return pd.DataFrame()
        
    def compute_h2h_stats(self, gamelog_a, gamelog_b):
        # Calculates H2H Stats by finding common games within 2 provided gamelogs
        
        empty_stats = {"game_count": 0, "error": "No H2H Games Found."}
        
        if gamelog_a.empty or gamelog_b.empty:
            return {"player:a": empty_stats, "player_b": empty_stats}
        
        # Find Common Game_ID's
        common_game_ids = pd.merge(gamelog_a, gamelog_b, on='Game_ID', suffixes=('_a', '_b'))['Game_ID']
        
        if common_game_ids.empty:
            return {"player_a": empty_stats, "player_b": empty_stats}
        
        # Filter Gamelogs for just the H2H Games
        h2h_games_a = gamelog_a[gamelog_a['Game_ID'].isin(common_game_ids)]
        h2h_games_b = gamelog_b[gamelog_b['Game_ID'].isin(common_game_ids)]
        
        # Aggregate stats for each player
        stats_a = self.aggregate_stats_from_df(h2h_games_a)
        stats_b = self.aggregate_stats_from_df(h2h_games_b)
        
        return {"player_a": stats_a, "player_b": stats_b}
    
    def aggregate_stats_from_df(self, stats_df):
        
        if stats_df.empty:
            return {"game_count": 0, "error": "No games to aggregate."}
        
        game_count = len(stats_df)
        total_stats = stats_df.sum(numeric_only=True)
        
        # Calculate Advanced Stats
        try:
            efg_pct = (total_stats['FGM'] + 0.5 * total_stats['FG3M']) / total_stats['FGA']
        except ZeroDivisionError:
            efg_pct = 0
            
        try:
            tsp_pct = total_stats['PTS'] / (2 * (total_stats['FGA'] + 0.44 * total_stats['FTA']))
        except ZeroDivisionError:
            tsp_pct = 0
            
        # Calculate Averages
        avg_cols = [
            'MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 
            'FTA', 'OREB', 'DREB', 'REB', 'AST', 'STL', 
            'BLK', 'TOV', 'PF', 'PTS'
        ]
        avg_stats = {}
        for col in avg_cols:
            total = pd.to_numeric(total_stats[col])
            if game_count == 0:
                avg = 0
            else:
                avg = total / game_count
            avg_stats[col] = round(avg, 1)
            
        return {
            "game_count": int(game_count),
            "avg_stats": avg_stats,
            "advanced_stats": {
                "efg_pct": round(efg_pct, 3),
                "tsp_pct": round(tsp_pct, 3),
            },
            "total_stats": total_stats.to_dict()
        }