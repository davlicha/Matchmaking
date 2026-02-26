class RatingCalculator:
    @staticmethod
    def calculate_new_mmr(winner_mmr: int, loser_mmr: int) -> tuple[int, int]:
        """Повертає новий MMR для переможця та переможеного"""
        return winner_mmr + 25, max(0, loser_mmr - 25)