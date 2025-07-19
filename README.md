# DynastyAnalyzer

A full-stack application for analyzing fantasy football dynasty leagues using the Sleeper API.

## Project Structure

```
DynastyAnalyzer/
├── backend/                # Python FastAPI backend
│   ├── app/               # Application source code
│   │   ├── main.py       # Main application entry point
│   │   └── services/     # External services integration
│   ├── tests/            # Test files
│   └── requirements.txt  # Python dependencies
│
└── frontend/             # React frontend
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Get User's Leagues
Retrieves all fantasy football leagues for a given Sleeper username.

```
GET /leagues/user/{username}
```

**Parameters**
- `username` (path parameter, string): The Sleeper username

**Response**
```json
[
  {
    "league_id": "123456",
    "name": "Dynasty Super League",
    "season": "2025",
    "status": "in_season",
    "settings": {
      "type": 2,
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
```

**Error Responses**
- `404 Not Found`: User not found
  ```json
  {
    "detail": "User not found"
  }
  ```

#### 2. Get League Rosters
Retrieves all rosters and league information for a specific league ID.

```
GET /leagues/{league_id}/rosters
```

**Parameters**
- `league_id` (path parameter, string): The Sleeper league ID

**Response**
```json
{
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
```

**Error Responses**
- `404 Not Found`: League not found
  ```json
  {
    "detail": "League not found"
  }
  ```

## Setup Instructions

### Backend
1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```
3. Run the server:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend
1. Install dependencies:
   ```
   cd frontend
   npm install
   ```
2. Start the development server:
   ```
   npm start
   ```