import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, UTC

import aio_pika
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from modules.players.api.router import get_player_service
from modules.players.api.router import router as players_router
from modules.players.api.router import repo


async def consume_match_events():
    while True:
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
            async with connection:
                channel = await connection.channel()
                exchange = await channel.declare_exchange("match_events", aio_pika.ExchangeType.FANOUT)
                player_exchange = await channel.declare_exchange("player_events", aio_pika.ExchangeType.FANOUT)
                queue = await channel.declare_queue("player_service_queue", durable=True)
                await queue.bind(exchange)

                print("[Consumer] Очікування подій...")
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            if message.type == "TICKET_CREATED":
                                payload = json.loads(message.body.decode())
                                player = repo.get_by_id(payload["player_id"])

                                response_payload = {"ticket_id": payload["ticket_id"]}

                                if player and player.tokens >= 10:
                                    player.tokens -= 10
                                    repo.save(player)
                                    print(f"[SAGA] Успіх. Знято токени. Залишок: {player.tokens}")
                                    status = "PAYMENT_SUCCESS"
                                else:
                                    print(f"[SAGA] Помилка. Недостатньо токенів у {payload['player_id']}")
                                    status = "PAYMENT_FAILED"

                                msg = aio_pika.Message(body=json.dumps(response_payload).encode(), type=status)
                                await player_exchange.publish(msg, routing_key="")

                            winner_id = payload.get("winner_id")
                            loser_id = payload.get("loser_id")
                            print(f"[Consumer] Отримано результат матчу: W: {winner_id}, L: {loser_id}")

                            svc = get_player_service()
                            svc.process_match_result(winner_id, loser_id)
        except Exception as e:
            print(f"[Consumer Error] Втрачено зв'язок з RabbitMQ. Перепідключення... {e}")
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(consume_match_events())
    yield
    task.cancel()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


def create_error_response(status_code: int, error_code: str, message: str, path: str):
    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message, "timestamp": datetime.now(UTC).isoformat(), "path": path}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return create_error_response(400, "BAD_REQUEST", str(exc), request.url.path)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response(400, "VALIDATION_ERROR", "Дані не пройшли валідацію", request.url.path)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return create_error_response(exc.status_code, error_code, str(exc.detail), request.url.path)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return create_error_response(500, "INTERNAL_SERVER_ERROR", "Щось пішло не так на сервері", request.url.path)


app.include_router(players_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "UP", "service": settings.app_name, "timestamp": datetime.now(UTC).isoformat()}
