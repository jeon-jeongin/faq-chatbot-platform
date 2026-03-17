from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    default_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    debug: bool = Field(default=True, validation_alias="DEBUG")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()