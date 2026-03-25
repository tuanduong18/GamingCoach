from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from riot_api import get_summoner_data
from ai_service import generate_coaching_advice

app = FastAPI(title="GamingCoach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CoachRequest(BaseModel):
    summoner_name: str
    match_data: List[Dict[str, Any]]
    game_type: str = "ALL"

@app.get("/api/matches")
def fetch_matches(summoner: str, region: str = "na1", gameType: str = "ALL"):
    """
    Fetches the summoner data and recent matches from the Riot API.
    `summoner` should be formatted as GameName#TagLine (e.g. Faker#KR1).
    `region` should be the server routing value (e.g. na1, euw1, kr).
    """
    if "#" not in summoner:
        raise HTTPException(status_code=400, detail="Summoner name must include TagLine (e.g., Name#Tag)")
    
    game_name, tag_line = summoner.split("#", 1)
    
    data = get_summoner_data(game_name, tag_line, region, gameType)
    if not data:
        raise HTTPException(status_code=404, detail="Summoner not found or API error")
        
    return data

@app.post("/api/coach")
def get_coaching_advice(req: CoachRequest):
    """
    Takes the structured match data and asks Gemini for coaching advice.
    """
    advice = generate_coaching_advice(req.summoner_name, req.match_data, req.game_type)
    return {"advice": advice}

@app.get("/")
def read_root():
    return {"status": "ok", "app": "GamingCoach API"}
