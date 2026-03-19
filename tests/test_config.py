"""Tests for configuration module."""

import json

from book_reading_assistant.config import Settings, save_config


def test_default_settings():
    settings = Settings(anthropic_api_key="test-key")
    assert settings.model == "claude-sonnet-4-20250514"
    assert settings.output_dir == "./output"
    assert settings.max_tokens == 200_000


def test_settings_from_kwargs():
    settings = Settings(
        anthropic_api_key="key",
        model="claude-opus-4-20250514",
        max_tokens=100_000,
    )
    assert settings.model == "claude-opus-4-20250514"
    assert settings.max_tokens == 100_000


def test_get_library_path_creates_dir(tmp_path):
    settings = Settings(
        anthropic_api_key="key",
        library_dir=str(tmp_path / "lib"),
    )
    path = settings.get_library_path()
    assert path.exists()
    assert path == tmp_path / "lib"


def test_get_output_path_creates_dir(tmp_path):
    settings = Settings(
        anthropic_api_key="key",
        output_dir=str(tmp_path / "out"),
    )
    path = settings.get_output_path()
    assert path.exists()


def test_save_config_creates_file(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(
        "book_reading_assistant.config.DEFAULT_CONFIG_PATH", config_path
    )
    save_config("model", "claude-opus-4-20250514")

    data = json.loads(config_path.read_text())
    assert data["model"] == "claude-opus-4-20250514"


def test_save_config_preserves_existing(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"output_dir": "/tmp/out"}))
    monkeypatch.setattr(
        "book_reading_assistant.config.DEFAULT_CONFIG_PATH", config_path
    )

    save_config("model", "claude-opus-4-20250514")

    data = json.loads(config_path.read_text())
    assert data["model"] == "claude-opus-4-20250514"
    assert data["output_dir"] == "/tmp/out"
