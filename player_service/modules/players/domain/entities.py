from dataclasses import dataclass
import uuid

@dataclass
class Player:
    id: str
    username: str
    mmr: int
    tokens: int

    @classmethod
    def create(cls, username: str) -> "Player":
        return cls(id=str(uuid.uuid4()), username=username, mmr=1000, tokens = 5)