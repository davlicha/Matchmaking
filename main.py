from fastapi import FastAPI
from modules.players.api.router import router as players_router
from modules.matchmaking.api.router import router as matchmaking_router
from modules.matches.api.router import router as matches_router

app = FastAPI(title="Matchmaking Modular Monolith")

app.include_router(players_router)
app.include_router(matchmaking_router)
app.include_router(matches_router)

@app.get("/")
def health_check():
    return {"status": "ok", "architecture": "Modular Monolith"}