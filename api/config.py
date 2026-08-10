from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_host: str = "http://127.0.0.1:11434"
    frontend_origin: str = "http://localhost:3000"
    default_model: str = "qwen2.5:0.5b"

    chroma_persist_dir: str = "../data/chroma"
    embedding_model_name: str = "nomic-ai/nomic-embed-text-v1.5"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()