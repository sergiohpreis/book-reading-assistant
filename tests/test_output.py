"""Tests for output formatting."""

from datetime import datetime

from book_reading_assistant.analyzer import AnalysisResult
from book_reading_assistant.output import save_analysis


def test_save_analysis(tmp_path):
    result = AnalysisResult(
        content="# Analysis\n\nGreat notes!",
        model="claude-sonnet-4-20250514",
        book_name="test_book",
        notes_name="notes.md",
        references=["ref1.pdf", "ref2.pdf"],
        timestamp=datetime(2025, 1, 15, 10, 30, 0),
        input_tokens=1000,
        output_tokens=500,
    )

    output_path = save_analysis(result, tmp_path)

    assert output_path.exists()
    assert "test_book_analysis_20250115_103000.md" == output_path.name

    content = output_path.read_text()
    assert "book: test_book" in content
    assert "model: claude-sonnet-4-20250514" in content
    assert "ref1.pdf" in content
    assert "# Analysis" in content


def test_save_analysis_creates_dir(tmp_path):
    result = AnalysisResult(
        content="Content",
        model="test",
        book_name="book",
        notes_name="notes.md",
        references=[],
    )

    output_dir = tmp_path / "nested" / "output"
    output_path = save_analysis(result, output_dir)
    assert output_path.exists()
