from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8001


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    words: str = "/words"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class MiddlewareConfig(BaseSettings):
    session_secret_key: str


class AuthJWTConfig(BaseSettings):
    private_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 1
    refresh_token_expire_days: int = 30


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 50

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class LangchainConfig(BaseModel):
    llm_api_key: SecretStr
    translation_prompt: str


class RabbitMQConfig(BaseModel):
    user: str
    password: str
    host: str
    port: str


class SMTPConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    from_: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    llm: LangchainConfig
    rabbitmq: RabbitMQConfig
    smtp: SMTPConfig
    middleware: MiddlewareConfig
    auth_jwt: AuthJWTConfig = AuthJWTConfig()


@lru_cache
def get_settings() -> "Settings":
    return Settings()


templates = Jinja2Templates(directory="templates")
