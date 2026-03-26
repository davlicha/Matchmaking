from ..application.interfaces import MatchRepository
from ..domain.entities import Match, OutboxEvent


class InMemoryMatchRepository(MatchRepository):
    def __init__(self):
        self._matches: dict[str, Match] = {}

    def save(self, match: Match) -> None:
        self._matches[match.id] = match

    def get_by_id(self, match_id: str) -> Match | None:
        return self._matches.get(match_id)


class InMemoryOutboxRepository:
    def __init__(self):
        self._events: dict[str, OutboxEvent] = {}

    def save(self, event: OutboxEvent) -> None:
        self._events[event.id] = event

    def get_unprocessed(self) -> list[OutboxEvent]:
        return [e for e in self._events.values() if not e.processed]


outbox_repo = InMemoryOutboxRepository()
