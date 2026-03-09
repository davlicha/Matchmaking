from fastapi import APIRouter, Depends, HTTPException
from core.config import settings
from ..application.dto import JoinQueueDTO, TicketResponseDTO, MatchResultDTO
from ..application.service import MatchmakingService
from ..infrastructure.repositories import InMemoryTicketRepository

from ...players.api.router import service as player_service_instance

router = APIRouter(prefix=f"{settings.api_v1_str}/matchmaking", tags=["Matchmaking"])

repo = InMemoryTicketRepository()
service = MatchmakingService(
    ticket_repo=repo,
    player_service=player_service_instance
)

def get_matchmaking_service():
    return service

@router.post("/join", response_model=TicketResponseDTO)
def join_queue(dto: JoinQueueDTO, svc: MatchmakingService = Depends(get_matchmaking_service)):
        return svc.join_queue(dto)

@router.post("/process", response_model=MatchResultDTO)
def process_queue(svc: MatchmakingService = Depends(get_matchmaking_service)):
    return svc.process_queue()