from pydantic import BaseModel
from typing import Optional

class CreateMatchDTO(BaseModel):
    player1_id: str
    player2_id: str

class FinishMatchDTO(BaseModel):
    winner_id: str

class MatchResponseDTO(BaseModel):
    id: str
    player1_id: str
    player2_id: str
    status: str
    winner_id: Optional[str]