from fastapi import APIRouter, Depends, HTTPException
from ..application.dto import CreatePlayerDTO, PlayerResponseDTO
from ..application.service import PlayerService
from ..infrastructure.repositories import InMemoryPlayerRepository

router = APIRouter(prefix="/players", tags=["Players"])

repo = InMemoryPlayerRepository()
service = PlayerService(repository=repo)

def get_player_service():
    return service

@router.post("/", response_model=PlayerResponseDTO)
def create_player(dto: CreatePlayerDTO, svc: PlayerService = Depends(get_player_service)):
    return svc.register_player(dto)

@router.get("/{player_id}", response_model=PlayerResponseDTO)
def get_player(player_id: str, svc: PlayerService = Depends(get_player_service)):
    player = svc.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
