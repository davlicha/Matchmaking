from .interfaces import TicketRepository
from .dto import JoinQueueDTO, TicketResponseDTO, MatchResultDTO
from ..domain.entities import Ticket
from ..domain.services import Matchmaker
from core.http_client import PlayerServiceClient
import circuitbreaker

class MatchmakingService:
    def __init__(self, ticket_repo: TicketRepository, player_client: PlayerServiceClient):
        self._ticket_repo = ticket_repo
        self._player_client = player_client

    async def join_queue(self, dto: JoinQueueDTO, correlation_id: str) -> TicketResponseDTO:
        try:
            # Отримуємо дані гравця через HTTP-клієнт
            player_data = await self._player_client.get_player(dto.player_id, correlation_id)
        except circuitbreaker.CircuitBreakerError:
            raise ValueError("Сервіс гравців перевантажений (Circuit Breaker). Спробуйте через 10 секунд.")
        except Exception as e:
            raise ValueError(f"Сервіс гравців тимчасово недоступний: {str(e)}")

        if not player_data:
            raise ValueError(f"Гравця з ID {dto.player_id} не знайдено")

        # player_data тепер це словник, тому звертаємось через ключі ["id"] та ["mmr"]
        ticket = Ticket.create(player_id=player_data["id"], player_mmr=player_data["mmr"])
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