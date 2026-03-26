from fastapi import APIRouter, Depends, HTTPException, Request
from ..application.dto import JoinQueueDTO, TicketResponseDTO, MatchResultDTO
from ..application.service import MatchmakingService
from ..infrastructure.repositories import InMemoryTicketRepository
from core.http_client import PlayerServiceClient

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

repo = InMemoryTicketRepository()
player_client_instance = PlayerServiceClient()
service = MatchmakingService(ticket_repo=repo, player_client=player_client_instance)

def get_matchmaking_service():
    return service

@router.post("/join", response_model=TicketResponseDTO)
async def join_queue(request: Request, dto: JoinQueueDTO, svc: MatchmakingService = Depends(get_matchmaking_service)):
    # Дістаємо ID трасування з поточного запиту
    correlation_id = request.state.correlation_id
    try:
        return await svc.join_queue(dto, correlation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/process", response_model=MatchResultDTO)
def process_queue(svc: MatchmakingService = Depends(get_matchmaking_service)):
    # Цей метод не робить HTTP-запитів, тому залишається синхронним
    return svc.process_queue()