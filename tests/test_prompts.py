"""Tests for prompt construction."""


from book_reading_assistant.prompts import build_system_prompt, build_user_content


def test_build_system_prompt():
    prompt = build_system_prompt()
    assert "fichamento" in prompt.lower()
    assert "reading notes" in prompt.lower()


def test_build_user_content_structure(tmp_path):
    """Test content block ordering: refs → book → notes."""
    # Create minimal PDFs
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
    ref1 = tmp_path / "ref1.pdf"
    ref2 = tmp_path / "ref2.pdf"
    book = tmp_path / "book.pdf"
    for p in [ref1, ref2, book]:
        p.write_bytes(pdf_content)

    content = build_user_content([ref1, ref2], book, "My reading notes")

    # 2 refs + 1 book + 1 notes text = 4 blocks
    assert len(content) == 4

    # First ref: no cache_control
    assert "cache_control" not in content[0]
    # Last ref: has cache_control
    assert content[1]["cache_control"] == {"type": "ephemeral"}
    # Book PDF
    assert content[2]["type"] == "document"
    # Notes text
    assert content[3]["type"] == "text"
    assert "My reading notes" in content[3]["text"]


def test_build_user_content_single_ref(tmp_path):
    """Single ref PDF should get cache_control."""
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
    ref = tmp_path / "ref.pdf"
    book = tmp_path / "book.pdf"
    for p in [ref, book]:
        p.write_bytes(pdf_content)

    content = build_user_content([ref], book, "Notes")
    assert content[0]["cache_control"] == {"type": "ephemeral"}
