import json

from .dto import CreateMatchDTO, MatchResponseDTO, FinishMatchDTO
from .interfaces import MatchRepository
from ..domain.entities import Match, OutboxEvent
from ..infrastructure.repositories import outbox_repo


class MatchService:
    def __init__(self, match_repo: MatchRepository):
        self._match_repo = match_repo

    def create_match(self, dto: CreateMatchDTO) -> MatchResponseDTO:
        match = Match.create(dto.player1_id, dto.player2_id)
        self._match_repo.save(match)
        return self._map_to_dto(match)

    async def finish_match(self, match_id: str, dto: FinishMatchDTO, correlation_id: str) -> MatchResponseDTO:
        match = self._match_repo.get_by_id(match_id)
        if not match:
            raise ValueError(f"Матч {match_id} не знайдено")

        loser_id = match.player1_id if match.player2_id == dto.winner_id else match.player2_id

        match.finish(dto.winner_id)
        self._match_repo.save(match)

        payload = json.dumps({"winner_id": dto.winner_id, "loser_id": loser_id, "correlation_id": correlation_id})
        event = OutboxEvent.create(event_type="MATCH_FINISHED", payload=payload)
        outbox_repo.save(event)

        return self._map_to_dto(match)

    def _map_to_dto(self, match: Match) -> MatchResponseDTO:
        return MatchResponseDTO(
            id=match.id,
            player1_id=match.player1_id,
            player2_id=match.player2_id,
            status=match.status,
            winner_id=match.winner_id
        )
