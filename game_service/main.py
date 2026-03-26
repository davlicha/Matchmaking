import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, UTC

import aio_pika
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from modules.matches.api.router import router as matches_router
from modules.matches.infrastructure.repositories import outbox_repo
from modules.matchmaking.api.router import router as matchmaking_router


async def relay_outbox_events():
    while True:
        try:
            unprocessed = outbox_repo.get_unprocessed()
            if unprocessed:
                connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
                async with connection:
                    channel = await connection.channel()
                    exchange = await channel.declare_exchange("match_events", aio_pika.ExchangeType.FANOUT)

                    for event in unprocessed:
                        message = aio_pika.Message(body=event.payload.encode())
                        await exchange.publish(message, routing_key="")
                        event.processed = True
                        print(f"[Relay] Відправлено подію {event.id}")
        except Exception as e:
            print(f"[Relay Error] Помилка брокера: {e}")

        await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(relay_outbox_events())
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


app.include_router(matchmaking_router)
app.include_router(matches_router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "UP", "service": settings.app_name, "timestamp": datetime.now(UTC).isoformat()}
