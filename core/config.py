from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Matchmaking System"
    debug_mode: bool = False
    port: int = 8000
    api_v1_str: str = "/api/v1"

    model_config = SettingsConfigDict(env_file="../.env")

settings = Settings()