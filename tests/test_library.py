"""Tests for library management."""

import pytest

from book_reading_assistant.library import add_pdfs, get_all_pdfs, list_pdfs, remove_pdf


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a minimal valid PDF."""
    pdf_content = (
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
    pdf_path = tmp_path / "technique.pdf"
    pdf_path.write_bytes(pdf_content)
    return pdf_path


def test_add_pdfs(tmp_library, sample_pdf):
    added = add_pdfs([sample_pdf], library_dir=tmp_library)
    assert added == ["technique.pdf"]
    assert (tmp_library / "technique.pdf").exists()


def test_add_nonexistent_pdf(tmp_library, tmp_path):
    with pytest.raises(FileNotFoundError):
        add_pdfs([tmp_path / "nope.pdf"], library_dir=tmp_library)


def test_add_non_pdf(tmp_library, tmp_path):
    txt = tmp_path / "file.txt"
    txt.write_text("not a pdf")
    with pytest.raises(ValueError, match="Not a PDF"):
        add_pdfs([txt], library_dir=tmp_library)


def test_remove_pdf(tmp_library, sample_pdf):
    add_pdfs([sample_pdf], library_dir=tmp_library)
    assert remove_pdf("technique.pdf", library_dir=tmp_library)
    assert not (tmp_library / "technique.pdf").exists()


def test_remove_nonexistent(tmp_library):
    assert not remove_pdf("nope.pdf", library_dir=tmp_library)


def test_list_pdfs(tmp_library, sample_pdf):
    add_pdfs([sample_pdf], library_dir=tmp_library)
    entries = list_pdfs(library_dir=tmp_library)
    assert len(entries) == 1
    assert entries[0].name == "technique.pdf"
    assert entries[0].pages == 1


def test_list_empty_library(tmp_library):
    assert list_pdfs(library_dir=tmp_library) == []


def test_get_all_pdfs(tmp_library, sample_pdf):
    add_pdfs([sample_pdf], library_dir=tmp_library)
    paths = get_all_pdfs(library_dir=tmp_library)
    assert len(paths) == 1
    assert paths[0].name == "technique.pdf"
