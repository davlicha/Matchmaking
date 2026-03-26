from fastapi import APIRouter, Depends, HTTPException, Request

from core.http_client import PlayerServiceClient
from ..application.dto import CreateMatchDTO, MatchResponseDTO, FinishMatchDTO
from ..application.service import MatchService
from ..infrastructure.repositories import InMemoryMatchRepository

router = APIRouter(prefix="/matches", tags=["Matches"])

repo = InMemoryMatchRepository()
player_client_instance = PlayerServiceClient()
service = MatchService(match_repo=repo)


def get_match_service():
    return service


@router.post("/", response_model=MatchResponseDTO)
def create_match(dto: CreateMatchDTO, svc: MatchService = Depends(get_match_service)):
    return svc.create_match(dto)


@router.post("/{match_id}/finish", response_model=MatchResponseDTO)
async def finish_match(match_id: str, dto: FinishMatchDTO, request: Request,
                       svc: MatchService = Depends(get_match_service)):
    correlation_id = request.state.correlation_id
    try:
        return await svc.finish_match(match_id, dto, correlation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
