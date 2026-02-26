from typing import List, Tuple
from .entities import Ticket


class Matchmaker:
    @staticmethod
    def find_match(queue: List[Ticket], mmr_tolerance: int = 50) -> Tuple[Ticket, Ticket] | None:
        """Шукає двох гравців з різницею в рейтингу не більше mmr_tolerance"""
        if len(queue) < 2:
            return None

        for i in range(len(queue)):
            for j in range(i + 1, len(queue)):
                if abs(queue[i].player_mmr - queue[j].player_mmr) <= mmr_tolerance:
                    return queue[i], queue[j]
        return None