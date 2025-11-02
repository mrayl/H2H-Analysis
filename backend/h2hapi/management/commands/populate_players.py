from django.core.management.base import BaseCommand
from h2hapi.models import Player
from nba_api.stats.static import players

class Command(BaseCommand):
    help = 'Populates the database with NBA players using nba-api'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Starting player population...")

        try:
            # This function call gets ALL players (active and historic)
            all_players = players.get_players()
            
            if not all_players:
                self.stderr.write(self.style.ERROR("Could not fetch any players from nba-api."))
                return
            
            players_added_count = 0
            players_updated_count = 0
            
            for player_data in all_players:
                if not player_data['is_active']:
                    continue # Skip players that aren't active
                
                obj, created = Player.objects.update_or_create(
                    api_id=player_data['id'],
                    defaults={
                        'first_name': player_data['first_name'],
                        'last_name': player_data['last_name'],
                    }
                )
                
                if created:
                    players_added_count += 1
                else:
                    players_updated_count += 1
                    
            self.stdout.write(self.style.SUCCESS(
                f"Successfully finished populating active players."
            ))
            self.stdout.write(f"Players Added: {players_added_count}")
            self.stdout.write(f"Players Updated: {players_updated_count}")
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
            self.stderr.write(
                "This might be a temporary connection issue to stats.nba.com."
            )