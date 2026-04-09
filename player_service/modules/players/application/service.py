from .dto import CreatePlayerDTO, PlayerResponseDTO
from .interfaces import PlayerRepository
from ..domain.entities import Player


class PlayerService:
    def __init__(self, repository: PlayerRepository):
        self._repository = repository

    def register_player(self, dto: CreatePlayerDTO) -> PlayerResponseDTO:
        player = Player.create(username=dto.username)
        self._repository.save(player)
        return PlayerResponseDTO(id=player.id, username=player.username, mmr=player.mmr, tokens=player.tokens)

    def get_player(self, player_id: str) -> PlayerResponseDTO | None:
        player = self._repository.get_by_id(player_id)
        if not player:
            return None
        return PlayerResponseDTO(id=player.id, username=player.username, mmr=player.mmr, tokens=player.tokens)

    def update_mmr(self, player_id: str, new_mmr: int) -> None:
        player = self._repository.get_by_id(player_id)
        if not player:
            raise ValueError("Гравця з таким ID не знайдено")
        player.mmr = new_mmr
        self._repository.save(player)

    def process_match_result(self, winner_id: str, loser_id: str) -> None:
        winner = self._repository.get_by_id(winner_id)
        loser = self._repository.get_by_id(loser_id)

        if winner and loser:
            winner.mmr += 25
            loser.mmr = max(0, loser.mmr - 25)
            self._repository.save(winner)
            self._repository.save(loser)
            print(f"[Player Service] MMR оновлено! Переможець: {winner.mmr}, Переможений: {loser.mmr}")
