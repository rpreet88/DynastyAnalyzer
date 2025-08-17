from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Union

from app.services import sleeper_api

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Dynasty Analyzer API"}

@app.get("/leagues/user/{username}", response_model=List[Dict])
async def get_user_leagues(username: str):
    """Get all leagues for a given Sleeper username"""
    leagues = await sleeper_api.get_user_leagues(username)
    if leagues is None:
        raise HTTPException(status_code=404, detail="User not found")
    return leagues

@app.get("/leagues/{league_id}/rosters", response_model=Dict[str, Union[Dict, List]])
async def get_league_rosters(league_id: str):
    """Get all rosters for a given league ID"""
    league_data = await sleeper_api.get_league_rosters(league_id)
    if league_data is None:
        raise HTTPException(status_code=404, detail="League not found")
    return league_data
