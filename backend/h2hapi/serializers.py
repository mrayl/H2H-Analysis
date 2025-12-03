from rest_framework import serializers
from .models import Player
from django.core.validators import RegexValidator

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['api_id', 'first_name', 'last_name']
        
class ComparisonRequestSerializer(serializers.Serializer):
    # Validated Input and Sanitizes Data
    
    player_a_id = serializers.IntegerField(
        min_value=1,
        required=True,
        help_text="NBA API ID for the first player"
    )
    
    player_b_id = serializers.IntegerField(
        min_value=1,
        required=True,
        help_text="NBA API ID for the second player"
    )
    
    # Stops XSS/Script Injection
    season = serializers.CharField(
        required=False,
        default="2025-26",
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{2}(\d{2})?$',
                message="Season must be in 'YYYY-YY' or 'YYYY-YYYY' format"
            )
        ]
    )
    
    def validator(self, data):
        # Cross-Field validation
        if data['player_a_id'] == data['player_b_id']:
            raise serializers.ValidationError("Cannot compare a player to themselves")
        return data