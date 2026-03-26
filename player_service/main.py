import uuid
from datetime import datetime, UTC
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from modules.players.api.router import router as players_router

app = FastAPI(title=settings.app_name, version="1.0.0")

# --- ЛАБА 3: Middleware для трасування (Correlation ID) ---
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

# --- ЛАБА 2: Централізована обробка помилок ---
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

# --- Підключення роутерів ---
app.include_router(players_router)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "UP", "service": settings.app_name, "timestamp": datetime.now(UTC).isoformat()}