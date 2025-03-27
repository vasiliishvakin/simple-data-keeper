import os
from enum import Enum

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.storage.enums import StorageDriverType

load_dotenv(".env")
load_dotenv(f".env.{os.getenv('APP_ENV', 'development')}", override=True)


class AppEnv(str, Enum):
    development = "development"
    production = "production"
    diagnostic = "diagnostic"
    testing = "testing"


class Settings(BaseSettings):
    env: AppEnv = Field(default=AppEnv.development)
    debug: bool = Field(default=True)
    storage_driver: StorageDriverType = Field(default=StorageDriverType.LOCAL)
    base_dir: str = Field(default="./storage")

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="allow")
