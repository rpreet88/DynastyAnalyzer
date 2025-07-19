from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch

from app.main import app

client = TestClient(app)

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
            "reserve": ["91011"]
        },
        {
            "roster_id": 2,
            "owner_id": "user456",
            "players": ["2345", "6789", "101112"],
            "starters": ["2345", "6789"],
            "reserve": ["101112"]
        }
    ]
}

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
        assert data["rosters"][0]["roster_id"] == 1
        assert data["rosters"][0]["owner_id"] == "user123"
        assert len(data["rosters"][0]["players"]) == 3
        assert len(data["rosters"][0]["starters"]) == 2

def test_get_user_leagues_user_not_found():
    """Test the error handling when a username is not found"""
    username = "nonexistentuser"
    
    # Mock the Sleeper API response to simulate user not found
    with patch("app.services.sleeper_api.get_user_leagues") as mock_get_leagues:
        mock_get_leagues.return_value = None
        
        response = client.get(f"/leagues/user/{username}")
        
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}
