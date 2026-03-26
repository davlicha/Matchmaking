from pydantic import BaseModel, Field
from typing import Optional

class JoinQueueDTO(BaseModel):
    player_id: str = Field(..., min_length=1, description="ID гравця для додавання в чергу")

class TicketResponseDTO(BaseModel):
    ticket_id: str
    player_id: str
    status: str

class MatchResultDTO(BaseModel):
    message: str
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None