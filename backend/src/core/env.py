from functools import cached_property

from pydantic import PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    USER: str
    PASSWORD: str
    DB: str
    HOST: str
    PORT: int = 5432
    SCHEME: str = "postgresql+asyncpg"

    @computed_field
    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.SCHEME,
            username=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=self.PORT,
            path=self.DB,
        )


class RedisSettings(BaseSettings):
    DSN: RedisDsn


class CORSSettings(BaseSettings):
    ALLOW_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]


class Settings(BaseSettings):
    DEBUG: bool = True
    POSTGRES: PostgresSettings
    REDIS: RedisSettings
    CORS: CORSSettings = CORSSettings()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        validate_default=True,
        ignored_types=(cached_property,),
        extra="allow",
        use_attribute_docstrings=True,
    )
