"""
Service module for interacting with the Sleeper API
"""
from typing import List, Dict, Optional, Union
import httpx
from datetime import datetime

SLEEPER_API_BASE_URL = "https://api.sleeper.app/v1"

async def get_user_leagues(username: str) -> Optional[List[Dict]]:
    """
    Fetch all leagues for a given Sleeper username
    """
    async with httpx.AsyncClient() as client:
        # First get the user ID
        user_response = await client.get(f"{SLEEPER_API_BASE_URL}/user/{username}")
        if user_response.status_code == 404:
            return None
        
        user_data = user_response.json()
        user_id = user_data["user_id"]
        
        # Then get all leagues for that user ID
        leagues_response = await client.get(f"{SLEEPER_API_BASE_URL}/user/{user_id}/leagues/nfl/2025")
        if leagues_response.status_code != 200:
            return None
            
        return leagues_response.json()

async def get_league_rosters(league_id: str) -> Optional[Dict[str, Union[Dict, List]]]:
    """
    Fetch league information and all rosters for a given league ID
    """
    async with httpx.AsyncClient() as client:
        # Get league info
        league_response = await client.get(f"{SLEEPER_API_BASE_URL}/league/{league_id}")
        if league_response.status_code == 404:
            return None
            
        league_info = league_response.json()
        
        # Get rosters
        rosters_response = await client.get(f"{SLEEPER_API_BASE_URL}/league/{league_id}/rosters")
        if rosters_response.status_code != 200:
            return None
            
        return {
            "league_info": league_info,
            "rosters": rosters_response.json()
        }

# Cache for player data
_player_cache = {}
_last_cache_update = None

async def get_players(player_ids: List[str]) -> Dict[str, Dict]:
    """
    Get player information for a list of player IDs.
    Returns a dictionary of player objects containing name, position, and age.
    """
    global _player_cache, _last_cache_update
    
    # Update cache if it's empty or older than 24 hours
    current_time = datetime.now()
    if not _player_cache or (
        _last_cache_update and (current_time - _last_cache_update).days >= 1
    ):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SLEEPER_API_BASE_URL}/players/nfl")
            if response.status_code == 200:
                _player_cache = response.json()
                _last_cache_update = current_time

    # Filter and transform the requested players
    players = {}
    
    for player_id in player_ids:
        if player_id in _player_cache:
            player = _player_cache[player_id]
            # Calculate age
            age = None
            birth_date = player.get("birth_date")
            if birth_date:
                try:
                    if isinstance(birth_date, str):
                        birth_date = int(birth_date)
                    birth_datetime = datetime.fromtimestamp(birth_date/1000)
                    age = current_time.year - birth_datetime.year
                    # Adjust age if birthday hasn't occurred this year yet
                    if current_time.month < birth_datetime.month or (current_time.month == birth_datetime.month and current_time.day < birth_datetime.day):
                        age -= 1
                except (ValueError, TypeError):
                    pass
            
            players[player_id] = {
                "name": f"{player.get('first_name', '')} {player.get('last_name', '')}".strip(),
                "position": player.get("position"),
                "age": age,
                "team": player.get("team"),
                "number": player.get("number"),
                "status": player.get("status"),
                "experience": player.get("years_exp")
            }
    
    return players