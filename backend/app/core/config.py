from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database config
    DB_URL: str = Field("", validation_alias="DB_URL")
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # LLM
    LLM_API_KEY: SecretStr
    TRANSLATION_PROMPT: str

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        extra="ignore",
    )

    @model_validator(mode="after")
    def populate_db_urls(self) -> "Settings":
        self.DB_URL = self.__construct_db_url()
        return self

    def __construct_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache
def get_settings() -> "Settings":
    return Settings()
