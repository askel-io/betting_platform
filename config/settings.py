from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = REPO_ROOT / ".env"


def _non_empty_str(value: object, fallback: str) -> str:
    if value is None:
        return fallback
    if isinstance(value, str) and not value.strip():
        return fallback
    return str(value)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Postgres credentials (docker-compose, не коммитить реальные значения)
    line_provider_postgres_user: str = "line_provider"
    line_provider_postgres_password: str = "line_provider"
    line_provider_postgres_db: str = "line_provider"

    bet_maker_postgres_user: str = "bet_maker"
    bet_maker_postgres_password: str = "bet_maker"
    bet_maker_postgres_db: str = "bet_maker"

    # Database URLs — локальная разработка
    line_provider_database_url: str = Field(
        default="postgresql+asyncpg://line_provider:line_provider@localhost:5433/line_provider",
        validation_alias=AliasChoices("LINE_PROVIDER_DATABASE_URL", "DATABASE_URL"),
    )
    bet_maker_database_url: str = Field(
        default="postgresql+asyncpg://bet_maker:bet_maker@localhost:5434/bet_maker",
        validation_alias=AliasChoices("BET_MAKER_DATABASE_URL", "DATABASE_URL"),
    )

    # Database URLs — docker-compose (внутренняя сеть)
    line_provider_database_url_docker: str = (
        "postgresql+asyncpg://line_provider:line_provider@line-provider-db:5432/line_provider"
    )
    bet_maker_database_url_docker: str = (
        "postgresql+asyncpg://bet_maker:bet_maker@bet-maker-db:5432/bet_maker"
    )

    # Тестовые БД
    line_provider_test_database_url: str = (
        "postgresql+asyncpg://line_provider:line_provider@localhost:5433/line_provider_test"
    )
    bet_maker_test_database_url: str = (
        "postgresql+asyncpg://bet_maker:bet_maker@localhost:5434/bet_maker_test"
    )

    # Kafka
    kafka_enabled: bool = True
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_bootstrap_servers_docker: str = "kafka:9093"
    kafka_event_finished_topic: str = "event.finished"
    kafka_consumer_group: str = "bet-maker"
    kafka_host: str = "localhost"
    kafka_port: int = 9092

    @field_validator("kafka_bootstrap_servers", mode="before")
    @classmethod
    def validate_kafka_bootstrap_servers(cls, value: object) -> str:
        return _non_empty_str(value, "localhost:9092")

    @field_validator("kafka_event_finished_topic", mode="before")
    @classmethod
    def validate_kafka_topic(cls, value: object) -> str:
        return _non_empty_str(value, "event.finished")

    @field_validator("kafka_consumer_group", mode="before")
    @classmethod
    def validate_kafka_consumer_group(cls, value: object) -> str:
        return _non_empty_str(value, "bet-maker")

    @field_validator("line_provider_url", mode="before")
    @classmethod
    def validate_line_provider_url(cls, value: object) -> str:
        return _non_empty_str(value, "http://localhost:8001")

    # Межсервисное взаимодействие
    line_provider_url: str = "http://localhost:8001"
    line_provider_url_docker: str = "http://line-provider:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
