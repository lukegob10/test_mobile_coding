from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    env: Literal['dev', 'prod'] = 'dev'
    log_level: str = 'INFO'

    api_host: str = '0.0.0.0'
    api_port: int = 8000

    cors_origins: str = 'http://localhost:8000'

    api_key: str | None = None
    allowed_api_keys: str | None = None

    vector_backend: Literal['qdrant', 'pgvector'] = 'qdrant'
    storage_backend: Literal['local', 's3'] = 'local'

    max_iters: int = 6
    max_context_chars: int = 8000
    timeout_seconds: int = 30
    max_top_k: int = 20

    upload_limit_mb: int = 25
    data_dir: str = './data'

    llm_provider: str = 'local'
    llm_model: str = 'rule-based'
    embed_provider: str = 'local'
    embed_model: str = 'hashing'

    rate_limit_per_minute: int = Field(default=30, ge=1)

    @property
    def cors_origins_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(',') if x.strip()]

    @property
    def api_keys(self) -> set[str]:
        keys: set[str] = set()
        if self.api_key:
            keys.add(self.api_key)
        if self.allowed_api_keys:
            keys.update({x.strip() for x in self.allowed_api_keys.split(',') if x.strip()})
        return keys


@lru_cache
def get_settings() -> Settings:
    return Settings()
