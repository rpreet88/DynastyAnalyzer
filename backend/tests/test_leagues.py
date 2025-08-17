from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch
from datetime import datetime

from app.main import app

client = TestClient(app)

MOCK_PLAYERS_RESPONSE = {
    "1234": {
        "first_name": "Patrick",
        "last_name": "Mahomes",
        "position": "QB",
        "team": "KC",
        "birth_date": "810604800000",  # Sept 10, 1995
        "years_exp": 6,
        "number": "15",
        "status": "Active"
    },
    "5678": {
        "first_name": "Justin",
        "last_name": "Jefferson",
        "position": "WR",
        "team": "MIN",
        "birth_date": "930096000000",  # June 24, 1999
        "years_exp": 3,
        "number": "18",
        "status": "Active"
    },
    "9012": {
        "first_name": "Rookie",
        "last_name": "Player",
        "position": "RB",
        "team": "FA",
        "birth_date": None,
        "years_exp": 0,
        "number": None,
        "status": "Active"
    }
}

MOCK_USER_LEAGUES_RESPONSE = [
    {
        "league_id": "123456",
        "name": "Dynasty Super League",
        "season": "2025",
        "status": "in_season",
        "settings": {
            "type": 2,  # dynasty
            "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "BN", "BN"],
            "teams": 12
        }
    },
    {
        "league_id": "789012",
        "name": "Dynasty Legends",
        "season": "2025",
        "status": "in_season",
        "settings": {
            "type": 2,
            "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "BN", "BN"],
            "teams": 10
        }
    }
]

MOCK_LEAGUE_ROSTERS_RESPONSE = {
    "league_info": {
        "league_id": "123456",
        "name": "Dynasty Super League",
        "season": "2025",
        "settings": {
            "type": 2,
            "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "BN", "BN"],
            "teams": 12
        }
    },
    "rosters": [
        {
            "roster_id": 1,
            "owner_id": "user123",
            "players": ["1234", "5678", "91011"],
            "starters": ["1234", "5678"],
            "bench": ["91011"]
        },
        {
            "roster_id": 2,
            "owner_id": "user456",
            "players": ["2345", "6789", "101112"],
            "starters": ["2345", "6789"],
            "bench": ["101112"]
        }
    ]
}

@patch("app.services.sleeper_api._player_cache", MOCK_PLAYERS_RESPONSE)
@patch("app.services.sleeper_api.datetime")
def test_get_players(mock_datetime):
    """Test getting player information"""
    # Mock current date to 2025
    mock_date = datetime(2025, 8, 17)
    mock_datetime.now.return_value = mock_date
    mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
    response = client.post("/players", json={"player_ids": ["1234", "5678"]})
    assert response.status_code == 200
    
    players = response.json()
    assert len(players) == 2
    
    # Check Mahomes
    mahomes = players["1234"]
    assert mahomes["name"] == "Patrick Mahomes"
    assert mahomes["position"] == "QB"
    assert mahomes["team"] == "KC"
    assert mahomes["number"] == "15"
    assert mahomes["status"] == "Active"
    assert mahomes["experience"] == 6
    assert mahomes["age"] == 29  # As of 2025 (test year) - 1995 (birth year)
    
    # Check Jefferson
    jefferson = players["5678"]
    assert jefferson["name"] == "Justin Jefferson"
    assert jefferson["position"] == "WR"
    assert jefferson["team"] == "MIN"
    assert jefferson["number"] == "18"
    assert jefferson["status"] == "Active"
    assert jefferson["experience"] == 3
    assert jefferson["age"] == 26  # As of 2025 (test year) - 1999 (birth year)

@patch("app.services.sleeper_api._player_cache", MOCK_PLAYERS_RESPONSE)
def test_get_players_with_missing_birth_date():
    """Test getting player information for a player without birth date"""
    response = client.post("/players", json={"player_ids": ["9012"]})
    assert response.status_code == 200
    
    players = response.json()
    rookie = players["9012"]
    assert rookie["name"] == "Rookie Player"
    assert rookie["age"] is None  # Age should be None when birth_date is not available
    assert rookie["position"] == "RB"
    assert rookie["team"] == "FA"
    assert rookie["status"] == "Active"
    assert rookie["experience"] == 0

@patch("app.services.sleeper_api.get_players")
def test_get_players_with_invalid_ids(mock_get_players):
    """Test getting player information with invalid IDs"""
    mock_get_players.return_value = {}
    response = client.post("/players", json={"player_ids": ["9999"]})
    assert response.status_code == 200
    assert response.json() == {}

def test_get_user_leagues():
    """Test getting all leagues for a given Sleeper username"""
    username = "testuser"
    
    # Mock the Sleeper API response
    with patch("app.services.sleeper_api.get_user_leagues") as mock_get_leagues:
        mock_get_leagues.return_value = MOCK_USER_LEAGUES_RESPONSE
        
        response = client.get(f"/leagues/user/{username}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the structure and content of the response
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify first league details
        assert data[0]["league_id"] == "123456"
        assert data[0]["name"] == "Dynasty Super League"
        assert data[0]["season"] == "2025"
        assert data[0]["settings"]["teams"] == 12
        
        # Verify second league details
        assert data[1]["league_id"] == "789012"
        assert data[1]["name"] == "Dynasty Legends"
        assert data[1]["settings"]["teams"] == 10

def test_get_league_rosters():
    """Test getting all rosters for a given league ID"""
    league_id = "123456"
    
    # Mock the Sleeper API response
    with patch("app.services.sleeper_api.get_league_rosters") as mock_get_rosters:
        mock_get_rosters.return_value = MOCK_LEAGUE_ROSTERS_RESPONSE
        
        response = client.get(f"/leagues/{league_id}/rosters")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the structure of the response
        assert "league_info" in data
        assert "rosters" in data
        
        # Verify league info
        assert data["league_info"]["league_id"] == league_id
        assert data["league_info"]["name"] == "Dynasty Super League"
        assert data["league_info"]["settings"]["teams"] == 12
        
        # Verify rosters
        assert len(data["rosters"]) == 2
        
        # Verify first roster
        roster1 = data["rosters"][0]
        assert roster1["roster_id"] == 1
        assert roster1["owner_id"] == "user123"
        assert len(roster1["players"]) == 3
        assert len(roster1["starters"]) == 2
        assert roster1["players"] == ["1234", "5678", "91011"]
        assert roster1["bench"] == ["91011"]
        
        # Verify second roster
        roster2 = data["rosters"][1]
        assert roster2["roster_id"] == 2
        assert roster2["owner_id"] == "user456"
        assert len(roster2["players"]) == 3
        assert len(roster2["starters"]) == 2
        assert roster2["players"] == ["2345", "6789", "101112"]
        assert roster2["bench"] == ["101112"]

def test_get_user_leagues_user_not_found():
    """Test the error handling when a username is not found"""
    username = "nonexistentuser"
    
    # Mock the Sleeper API response to simulate user not found
    with patch("app.services.sleeper_api.get_user_leagues") as mock_get_leagues:
        mock_get_leagues.return_value = None
        
        response = client.get(f"/leagues/user/{username}")
        
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}
