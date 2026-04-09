from dataclasses import dataclass
import uuid
from datetime import datetime, UTC

@dataclass
class Ticket:
    id: str
    player_id: str
    player_mmr: int
    created_at: datetime
    status: str = "PENDING"

    @classmethod
    def create(cls, player_id: str, player_mmr: int) -> "Ticket":
        return cls(
            id=str(uuid.uuid4()),
            player_id=player_id,
            player_mmr=player_mmr,
            created_at=datetime.now(UTC),
            status="PENDING"
        )