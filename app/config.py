import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

dir_path = os.path.dirname(os.path.realpath(__file__))


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(dir_path, "../.env"), env_file_encoding="utf-8")

    MODE: Literal["DEV", "PROD"]
    WILDBOX_TOKEN: str
    X_API_KEY: str


config = Config()

if config.MODE == "PROD":
    redis_path = "redis://redis_ai_seo_parser:6379/0"
else:
    redis_path = "redis://127.0.0.1:6379/0"
