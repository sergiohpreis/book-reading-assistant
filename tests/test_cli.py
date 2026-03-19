"""Tests for CLI commands."""


from typer.testing import CliRunner

from book_reading_assistant.cli import app

runner = CliRunner()


def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Book Reading Assistant" in result.output


def test_library_list_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "book_reading_assistant.cli.list_pdfs",
        lambda: [],
    )
    result = runner.invoke(app, ["library", "list"])
    assert result.exit_code == 0
    assert "empty" in result.output.lower()


def test_analyze_missing_book(tmp_path):
    notes = tmp_path / "notes.md"
    notes.write_text("Some notes")
    result = runner.invoke(app, ["analyze", "/nonexistent/book.pdf", str(notes)])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_config_show(monkeypatch):
    from book_reading_assistant.config import Settings

    mock_settings = Settings(anthropic_api_key="sk-test-1234")
    monkeypatch.setattr(
        "book_reading_assistant.cli.get_settings",
        lambda: mock_settings,
    )

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "claude-sonnet-4-20250514" in result.output


def test_config_set(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(
        "book_reading_assistant.config.DEFAULT_CONFIG_PATH", config_path
    )

    result = runner.invoke(app, ["config", "set", "model", "claude-opus-4-20250514"])
    assert result.exit_code == 0
    assert "claude-opus-4-20250514" in result.output


def test_config_set_invalid_key():
    result = runner.invoke(app, ["config", "set", "invalid_key", "value"])
    assert result.exit_code == 1
    assert "Invalid key" in result.output
