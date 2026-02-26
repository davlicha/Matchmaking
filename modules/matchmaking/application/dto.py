from pydantic import BaseModel
from typing import Optional

class JoinQueueDTO(BaseModel):
    player_id: str

class TicketResponseDTO(BaseModel):
    ticket_id: str
    player_id: str
    status: str

class MatchResultDTO(BaseModel):
    message: str
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None