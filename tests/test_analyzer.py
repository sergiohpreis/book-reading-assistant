"""Tests for the analyzer module."""

from unittest.mock import MagicMock, patch

import pytest

from book_reading_assistant.analyzer import (
    AnalysisResult,
    TokenBudgetError,
    analyze,
    estimate_total_tokens,
)
from book_reading_assistant.config import Settings


@pytest.fixture
def pdf_content():
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n193\n%%EOF"
    )


@pytest.fixture
def setup_files(tmp_path, pdf_content):
    """Create test PDF and notes files."""
    book = tmp_path / "book.pdf"
    book.write_bytes(pdf_content)

    notes = tmp_path / "notes.md"
    notes.write_text("# My Reading Notes\n\nSome observations about the book.")

    ref = tmp_path / "library" / "ref.pdf"
    ref.parent.mkdir()
    ref.write_bytes(pdf_content)

    return book, notes, ref


def test_estimate_total_tokens(setup_files):
    book, notes, ref = setup_files
    notes_text = notes.read_text()
    total = estimate_total_tokens([ref], book, notes_text)
    # 1 ref page + 1 book page = 2 × 2250 + notes chars / 4
    assert total > 0


def test_token_budget_error():
    err = TokenBudgetError(500_000, 200_000)
    assert "500,000" in str(err)
    assert "200,000" in str(err)


def test_analyze_no_refs(tmp_path, pdf_content):
    book = tmp_path / "book.pdf"
    book.write_bytes(pdf_content)
    notes = tmp_path / "notes.md"
    notes.write_text("Some notes")

    settings = Settings(
        anthropic_api_key="test",
        library_dir=str(tmp_path / "empty_lib"),
    )
    (tmp_path / "empty_lib").mkdir()

    with pytest.raises(ValueError, match="No reference PDFs"):
        analyze(book, notes, settings=settings)


def test_analyze_empty_notes(setup_files):
    book, notes, ref = setup_files
    notes.write_text("")

    settings = Settings(
        anthropic_api_key="test",
        library_dir=str(ref.parent),
    )

    with pytest.raises(ValueError, match="empty"):
        analyze(book, notes, settings=settings)


@patch("book_reading_assistant.analyzer.anthropic.Anthropic")
def test_analyze_success(mock_anthropic_cls, setup_files):
    book, notes, ref = setup_files

    # Mock API response
    mock_response = MagicMock()
    mock_response.content = [MagicMock(type="text", text="Great analysis!")]
    mock_response.usage.input_tokens = 1000
    mock_response.usage.output_tokens = 500

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_client

    settings = Settings(
        anthropic_api_key="test-key",
        library_dir=str(ref.parent),
        max_tokens=200_000,
    )

    result = analyze(book, notes, settings=settings)

    assert isinstance(result, AnalysisResult)
    assert result.content == "Great analysis!"
    assert result.model == "claude-sonnet-4-20250514"
    assert result.book_name == "book"
    assert result.input_tokens == 1000
    assert result.output_tokens == 500
