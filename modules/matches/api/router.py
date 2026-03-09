from fastapi import APIRouter, Depends, HTTPException
from core.config import settings
from ..application.dto import CreateMatchDTO, MatchResponseDTO, FinishMatchDTO
from ..application.service import MatchService
from ..infrastructure.repositories import InMemoryMatchRepository

from ...players.api.router import service as player_service_instance

router = APIRouter(prefix=f"{settings.api_v1_str}/matches", tags=["Matches"])

repo = InMemoryMatchRepository()
service = MatchService(match_repo=repo, player_service=player_service_instance)

def get_match_service():
    return service

@router.post("/", response_model=MatchResponseDTO)
def create_match(dto: CreateMatchDTO, svc: MatchService = Depends(get_match_service)):
    return svc.create_match(dto)

@router.post("/{match_id}/finish", response_model=MatchResponseDTO)
def finish_match(match_id: str, dto: FinishMatchDTO, svc: MatchService = Depends(get_match_service)):
        return svc.finish_match(match_id, dto)
