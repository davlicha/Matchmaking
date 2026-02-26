from ..domain.entities import Player
from ..application.interfaces import PlayerRepository

class InMemoryPlayerRepository(PlayerRepository):
    def __init__(self):
        self._db: dict[str, Player] = {}

    def save(self, player: Player) -> None:
        self._db[player.id] = player

    def get_by_id(self, player_id: str) -> Player | None:
        return self._db.get(player_id)