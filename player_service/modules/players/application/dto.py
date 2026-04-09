from pydantic import BaseModel, Field

class CreatePlayerDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Унікальне ім'я гравця (від 3 до 20 символів)")

class PlayerResponseDTO(BaseModel):
    id: str
    username: str
    mmr: int
    tokens: int

class UpdateMmrDTO(BaseModel):
    new_mmr: int = Field(..., description="Нове значення рейтингу гравця після матчу")