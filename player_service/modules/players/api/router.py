from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Request
from ..application.dto import CreatePlayerDTO, PlayerResponseDTO, UpdateMmrDTO
from ..application.service import PlayerService
from ..infrastructure.repositories import InMemoryPlayerRepository

router = APIRouter(prefix=f"{settings.api_v1_str}/players", tags=["Players"])

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

@router.patch("/{player_id}/mmr", tags=["Players"])
def update_player_mmr(
    player_id: str,
    dto: UpdateMmrDTO,
    svc: PlayerService = Depends(get_player_service)
):
    try:
        svc.update_mmr(player_id, dto.new_mmr)
        return {"message": "MMR успішно оновлено", "player_id": player_id, "new_mmr": dto.new_mmr}
    except ValueError as e:
        # Якщо гравець не знайдений, повертаємо 404
        raise HTTPException(status_code=404, detail=str(e))
