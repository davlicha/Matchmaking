from pydantic import BaseModel, Field
from typing import Optional

class CreateMatchDTO(BaseModel):
    player1_id: str = Field(..., min_length=1, description="ID першого гравця")
    player2_id: str = Field(..., min_length=1, description="ID другого гравця")

class FinishMatchDTO(BaseModel):
    winner_id: str = Field(..., min_length=1, description="ID переможця матчу")

class MatchResponseDTO(BaseModel):
    id: str
    player1_id: str
    player2_id: str
    status: str
    winner_id: Optional[str]