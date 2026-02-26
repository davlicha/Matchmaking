from fastapi import APIRouter, Depends, HTTPException
from ..application.dto import JoinQueueDTO, TicketResponseDTO, MatchResultDTO
from ..application.service import MatchmakingService
from ..infrastructure.repositories import InMemoryTicketRepository

from ...players.api.router import service as player_service_instance

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

repo = InMemoryTicketRepository()
service = MatchmakingService(
    ticket_repo=repo,
    player_service=player_service_instance
)

def get_matchmaking_service():
    return service

@router.post("/join", response_model=TicketResponseDTO)
def join_queue(dto: JoinQueueDTO, svc: MatchmakingService = Depends(get_matchmaking_service)):
    try:
        return svc.join_queue(dto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/process", response_model=MatchResultDTO)
def process_queue(svc: MatchmakingService = Depends(get_matchmaking_service)):
    return svc.process_queue()