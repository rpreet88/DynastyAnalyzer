"""
Service module for interacting with the Sleeper API
"""
from typing import List, Dict, Optional, Union
import httpx

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
