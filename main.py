from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, UTC
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from modules.players.api.router import router as players_router
from modules.matchmaking.api.router import router as matchmaking_router
from modules.matches.api.router import router as matches_router

app = FastAPI(
    title=settings.app_name,
    description="REST API для системи матчмейкінгу",
    version="1.0.0",
)

app.include_router(players_router)
app.include_router(matchmaking_router)
app.include_router(matches_router)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "UP",
        "app": settings.app_name,
        "timestamp": datetime.now(UTC).isoformat()
    }


def create_error_response(status_code: int, error_code: str, message: str, path: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": error_code,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat(),
            "path": path
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return create_error_response(400, "BUSINESS_LOGIC_ERROR", str(exc), request.url.path)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
    return create_error_response(400, "VALIDATION_ERROR", str(errors), request.url.path)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return create_error_response(500, "INTERNAL_SERVER_ERROR", "Щось пішло не так на сервері", request.url.path)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return create_error_response(exc.status_code, error_code, str(exc.detail), request.url.path)
