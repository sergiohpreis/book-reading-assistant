"""Configuration management using pydantic-settings."""

import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_LIBRARY_DIR = Path.home() / ".config" / "book-reading-assistant" / "library"
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "book-reading-assistant" / "config.json"


class Settings(BaseSettings):
    """Application settings loaded from env vars, .env file, and config file."""

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Claude model to use",
    )
    output_dir: str = Field(default="./output", description="Default output directory")
    library_dir: str = Field(
        default=str(DEFAULT_LIBRARY_DIR),
        description="Reference library directory",
    )
    max_tokens: int = Field(
        default=200_000,
        description="Maximum token budget for API calls",
    )

    @classmethod
    def load(cls) -> "Settings":
        """Load settings with config file values as base, overridden by env vars."""
        config_data = {}
        if DEFAULT_CONFIG_PATH.exists():
            config_data = json.loads(DEFAULT_CONFIG_PATH.read_text())
        return cls(**config_data)

    def get_library_path(self) -> Path:
        """Return the library directory as a Path, creating it if needed."""
        path = Path(self.library_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_output_path(self) -> Path:
        """Return the output directory as a Path, creating it if needed."""
        path = Path(self.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


def save_config(key: str, value: str) -> None:
    """Persist a config key-value pair to the config file."""
    DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    config_data = {}
    if DEFAULT_CONFIG_PATH.exists():
        config_data = json.loads(DEFAULT_CONFIG_PATH.read_text())

    config_data[key] = value
    DEFAULT_CONFIG_PATH.write_text(json.dumps(config_data, indent=2))


def get_settings() -> Settings:
    """Get application settings."""
    return Settings.load()
