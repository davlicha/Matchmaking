from typing import List
from ..domain.entities import Ticket
from ..application.interfaces import TicketRepository

class InMemoryTicketRepository(TicketRepository):
    def __init__(self):
        self._tickets: dict[str, Ticket] = {}

    def add(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    def remove(self, ticket_id: str) -> None:
        if ticket_id in self._tickets:
            del self._tickets[ticket_id]

    def get_all(self) -> List[Ticket]:
        return list(self._tickets.values())