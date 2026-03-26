import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional


@dataclass
class Match:
    id: str
    player1_id: str
    player2_id: str
    status: str  # "IN_PROGRESS", "FINISHED"
    created_at: datetime
    winner_id: Optional[str] = None

    @classmethod
    def create(cls, player1_id: str, player2_id: str) -> "Match":
        return cls(
            id=str(uuid.uuid4()),
            player1_id=player1_id,
            player2_id=player2_id,
            status="IN_PROGRESS",
            created_at=datetime.now(UTC)
        )

    def finish(self, winner_id: str):
        if winner_id not in [self.player1_id, self.player2_id]:
            raise ValueError("Переможцем може бути лише учасник матчу!")
        self.winner_id = winner_id
        self.status = "FINISHED"


@dataclass
class OutboxEvent:
    id: str
    event_type: str
    payload: str  # JSON рядок
    processed: bool = False
    created_at: datetime = None

    @classmethod
    def create(cls, event_type: str, payload: str) -> "OutboxEvent":
        return cls(id=str(uuid.uuid4()), event_type=event_type, payload=payload, created_at=datetime.now(UTC))
