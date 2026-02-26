from pydantic import BaseModel

class CreatePlayerDTO(BaseModel):
    username: str

class PlayerResponseDTO(BaseModel):
    id: str
    username: str
    mmr: int