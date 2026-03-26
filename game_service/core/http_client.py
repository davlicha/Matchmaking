import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from circuitbreaker import circuit
from .config import settings


class PlayerServiceClient:
    def __init__(self):
        self.base_url = settings.player_service_url
        self.timeout = 2.0  # ТАЙМАУТ: чекаємо максимум 2 секунди (Пункт 3.1)

    # CIRCUIT BREAKER: Якщо 3 рази поспіль помилка, "розриваємо ланцюг" на 10 секунд (Пункт 3.3)
    @circuit(failure_threshold=3, recovery_timeout=10)
    # RETRIES: Робимо 3 спроби з інтервалом в 1 секунду, якщо сервіс не відповідає (Пункт 3.2)
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def get_player(self, player_id: str, correlation_id: str):
        headers = {"X-Correlation-ID": correlation_id}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/players/{player_id}", headers=headers)

            if response.status_code == 404:
                return None
            response.raise_for_status()  # Викине помилку, якщо статус 500 тощо
            return response.json()

    # Аналогічний метод для оновлення MMR після матчу
    @circuit(failure_threshold=3, recovery_timeout=10)
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def update_mmr(self, player_id: str, new_mmr: int, correlation_id: str):
        headers = {"X-Correlation-ID": correlation_id}
        payload = {"new_mmr": new_mmr}  # Тобі треба буде додати ендпоінт PATCH або PUT в player_service

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.patch(f"{self.base_url}/players/{player_id}/mmr", json=payload, headers=headers)
            response.raise_for_status()