from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    UI_PORT: int = 8000
    API_PORT: int = 8001
    API_BASE: str = f"http://localhost:{API_PORT}/api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
