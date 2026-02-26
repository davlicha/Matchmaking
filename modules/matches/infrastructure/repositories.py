from ..domain.entities import Match
from ..application.interfaces import MatchRepository

class InMemoryMatchRepository(MatchRepository):
    def __init__(self):
        self._matches: dict[str, Match] = {}

    def save(self, match: Match) -> None:
        self._matches[match.id] = match

    def get_by_id(self, match_id: str) -> Match | None:
        return self._matches.get(match_id)