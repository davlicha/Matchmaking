from modules.players.application.dto import PlayerResponseDTO
from .interfaces import PlayerRepository
from .dto import CreatePlayerDTO, PlayerResponseDTO
from ..domain.entities import Player

class PlayerService:
    def __init__(self, repository: PlayerRepository):
        self._repository = repository

    def register_player(self, dto: CreatePlayerDTO) -> PlayerResponseDTO:
        player = Player.create(username=dto.username)
        self._repository.save(player)
        return PlayerResponseDTO(id=player.id, username=player.username, mmr=player.mmr)

    def get_player(self, player_id: str) -> PlayerResponseDTO | None:
        player = self._repository.get_by_id(player_id)
        if not player:
            return None
        return PlayerResponseDTO(id=player.id, username=player.username, mmr=player.mmr)

    def update_mmr(self, player_id: str, new_mmr: int) -> None:
        player = self._repository.get_by_id(player_id)
        if not player:
            raise ValueError("Гравця з таким ID не знайдено")
        player.mmr = new_mmr
        self._repository.save(player)
