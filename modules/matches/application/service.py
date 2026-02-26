from .interfaces import MatchRepository
from .dto import CreateMatchDTO, MatchResponseDTO, FinishMatchDTO
from ..domain.entities import Match
from ..domain.services import RatingCalculator

from ...players.application.service import PlayerService

class MatchService:
    def __init__(self, match_repo: MatchRepository, player_service: PlayerService):
        self._match_repo = match_repo
        self._player_service = player_service

    def create_match(self, dto: CreateMatchDTO) -> MatchResponseDTO:
        match = Match.create(dto.player1_id, dto.player2_id)
        self._match_repo.save(match)
        return self._map_to_dto(match)

    def finish_match(self, match_id: str, dto: FinishMatchDTO) -> MatchResponseDTO:
        match = self._match_repo.get_by_id(match_id)
        if not match:
            raise ValueError(f"Матч {match_id} не знайдено")
        if match.status == "FINISHED":
            raise ValueError("Матч вже завершено")

        match.finish(dto.winner_id)
        self._match_repo.save(match)

        loser_id = match.player1_id if match.player2_id == dto.winner_id else match.player2_id
        winner = self._player_service.get_player(dto.winner_id)
        loser = self._player_service.get_player(loser_id)

        new_winner_mmr, new_loser_mmr = RatingCalculator.calculate_new_mmr(winner.mmr, loser.mmr)

        self._player_service.update_mmr(winner.id, new_winner_mmr)
        self._player_service.update_mmr(loser.id, new_loser_mmr)

        return self._map_to_dto(match)

    def _map_to_dto(self, match: Match) -> MatchResponseDTO:
        return MatchResponseDTO(
            id=match.id,
            player1_id=match.player1_id,
            player2_id=match.player2_id,
            status=match.status,
            winner_id=match.winner_id
        )