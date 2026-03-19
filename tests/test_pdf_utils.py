"""Tests for PDF utilities."""

import base64

import pytest

from book_reading_assistant.pdf_utils import (
    TOKENS_PER_PAGE,
    build_pdf_content_block,
    encode_pdf_to_base64,
    estimate_tokens,
    get_page_count,
    parse_page_ranges,
)


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a minimal valid PDF for testing."""
    # Minimal valid PDF with 1 page
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td (Hello World) Tj ET\nendstream\nendobj\n"
        b"xref\n0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000206 00000 n \n"
        b"trailer<</Size 5/Root 1 0 R>>\n"
        b"startxref\n302\n%%EOF"
    )
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(pdf_content)
    return pdf_path


def test_encode_pdf_to_base64(sample_pdf):
    result = encode_pdf_to_base64(sample_pdf)
    # Should be valid base64
    decoded = base64.standard_b64decode(result)
    assert decoded == sample_pdf.read_bytes()


def test_get_page_count(sample_pdf):
    assert get_page_count(sample_pdf) == 1


def test_estimate_tokens(sample_pdf):
    assert estimate_tokens(sample_pdf) == TOKENS_PER_PAGE


def test_parse_page_ranges_single():
    assert parse_page_ranges("5", 10) == [4]  # 0-indexed


def test_parse_page_ranges_range():
    assert parse_page_ranges("1-3", 10) == [0, 1, 2]


def test_parse_page_ranges_multiple():
    result = parse_page_ranges("1-3,7-8", 10)
    assert result == [0, 1, 2, 6, 7]


def test_parse_page_ranges_clamps_to_total():
    result = parse_page_ranges("1-100", 5)
    assert result == [0, 1, 2, 3, 4]


def test_build_pdf_content_block(sample_pdf):
    block = build_pdf_content_block(sample_pdf)
    assert block["type"] == "document"
    assert block["source"]["type"] == "base64"
    assert block["source"]["media_type"] == "application/pdf"
    assert "cache_control" not in block


def test_build_pdf_content_block_with_cache(sample_pdf):
    block = build_pdf_content_block(sample_pdf, cache_control=True)
    assert block["cache_control"] == {"type": "ephemeral"}
