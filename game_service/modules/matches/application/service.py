from .interfaces import MatchRepository
from .dto import CreateMatchDTO, MatchResponseDTO, FinishMatchDTO
from ..domain.entities import Match
from ..domain.services import RatingCalculator
from core.http_client import PlayerServiceClient
import circuitbreaker

class MatchService:
    def __init__(self, match_repo: MatchRepository, player_client: PlayerServiceClient):
        self._match_repo = match_repo
        self._player_client = player_client

    def create_match(self, dto: CreateMatchDTO) -> MatchResponseDTO:
        match = Match.create(dto.player1_id, dto.player2_id)
        self._match_repo.save(match)
        return self._map_to_dto(match)

    async def finish_match(self, match_id: str, dto: FinishMatchDTO, correlation_id: str) -> MatchResponseDTO:
        match = self._match_repo.get_by_id(match_id)
        if not match:
            raise ValueError(f"Матч {match_id} не знайдено")
        if match.status == "FINISHED":
            raise ValueError("Матч вже завершено")

        loser_id = match.player1_id if match.player2_id == dto.winner_id else match.player2_id

        try:
            winner = await self._player_client.get_player(dto.winner_id, correlation_id)
            loser = await self._player_client.get_player(loser_id, correlation_id)

            if not winner or not loser:
                raise ValueError("Одного з гравців не знайдено в системі")

            new_winner_mmr, new_loser_mmr = RatingCalculator.calculate_new_mmr(winner["mmr"], loser["mmr"])

            await self._player_client.update_mmr(winner["id"], new_winner_mmr, correlation_id)
            await self._player_client.update_mmr(loser["id"], new_loser_mmr, correlation_id)

        except circuitbreaker.CircuitBreakerError:
            raise ValueError("Сервіс гравців перевантажений. Не вдалося оновити рейтинг. Спробуйте пізніше.")
        except Exception as e:
            raise ValueError(f"Сервіс гравців недоступний: {str(e)}")

        match.finish(dto.winner_id)
        self._match_repo.save(match)

        return self._map_to_dto(match)

    def _map_to_dto(self, match: Match) -> MatchResponseDTO:
        return MatchResponseDTO(
            id=match.id,
            player1_id=match.player1_id,
            player2_id=match.player2_id,
            status=match.status,
            winner_id=match.winner_id
        )