from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Game Service"
    port: int = 8002
    api_v1_str: str = "/api/v1"

    player_service_url: str = "http://127.0.0.1:8001/api/v1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()