from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    app_name: str = "FastAPI Social"
    admin_email: str = "mahmoudbintokura@gmail.com"


class DevConfig(GlobalConfig):
    ENV_STATE: str = "dev"
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    ENV_STATE: str = "test"
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True
    model_config = SettingsConfigDict(env_prefix="TEST_")


class ProdConfig(GlobalConfig):
    ENV_STATE: str = "prod"
    model_config = SettingsConfigDict(env_prefix="PROD_")


@lru_cache()
def get_config(env_state: Optional[str] = None):
    if env_state == "dev":
        return DevConfig()
    elif env_state == "test":
        return TestConfig()
    elif env_state == "prod":
        return ProdConfig()
    else:
        return GlobalConfig()


config = get_config(BaseConfig().ENV_STATE)
