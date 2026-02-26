from .interfaces import TicketRepository
from .dto import JoinQueueDTO, TicketResponseDTO, MatchResultDTO
from ..domain.entities import Ticket
from ..domain.services import Matchmaker

from ...players.application.service import PlayerService


class MatchmakingService:
    def __init__(self, ticket_repo: TicketRepository, player_service: PlayerService):
        self._ticket_repo = ticket_repo
        self._player_service = player_service

    def join_queue(self, dto: JoinQueueDTO) -> TicketResponseDTO:
        player = self._player_service.get_player(dto.player_id)
        if not player:
            raise ValueError(f"Гравця з ID {dto.player_id} не знайдено")

        ticket = Ticket.create(player_id=player.id, player_mmr=player.mmr)
        self._ticket_repo.add(ticket)

        return TicketResponseDTO(ticket_id=ticket.id, player_id=ticket.player_id, status="In Queue")

    def process_queue(self) -> MatchResultDTO:
        queue = self._ticket_repo.get_all()

        match = Matchmaker.find_match(queue)

        if match:
            ticket1, ticket2 = match
            self._ticket_repo.remove(ticket1.id)
            self._ticket_repo.remove(ticket2.id)

            return MatchResultDTO(
                message="Знайдено матч!",
                player1_id=ticket1.player_id,
                player2_id=ticket2.player_id
            )

        return MatchResultDTO(message="В черзі недостатньо гравців або немає підходящих по MMR")