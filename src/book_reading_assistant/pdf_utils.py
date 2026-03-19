"""PDF handling utilities: encoding, extraction, and token estimation."""

import base64
from pathlib import Path

from pypdf import PdfReader

TOKENS_PER_PAGE = 2250


def encode_pdf_to_base64(path: Path) -> str:
    """Encode a PDF file to base64 string."""
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def get_page_count(path: Path) -> int:
    """Return the number of pages in a PDF."""
    reader = PdfReader(path)
    return len(reader.pages)


def estimate_tokens(path: Path) -> int:
    """Estimate token count for a PDF based on page count."""
    return get_page_count(path) * TOKENS_PER_PAGE


def extract_text(path: Path, pages: list[int] | None = None) -> str:
    """Extract text from a PDF, optionally from specific pages (0-indexed)."""
    reader = PdfReader(path)
    if pages is None:
        pages = list(range(len(reader.pages)))

    text_parts = []
    for page_num in pages:
        if 0 <= page_num < len(reader.pages):
            text = reader.pages[page_num].extract_text()
            if text:
                text_parts.append(text)
    return "\n\n".join(text_parts)


def parse_page_ranges(page_spec: str, total_pages: int) -> list[int]:
    """Parse a page range spec like '1-50,100-150' into 0-indexed page numbers."""
    pages: list[int] = []
    for part in page_spec.split(","):
        part = part.strip()
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str) - 1  # Convert to 0-indexed
            end = int(end_str)  # Inclusive, so no -1
            pages.extend(range(max(0, start), min(end, total_pages)))
        else:
            page = int(part) - 1  # Convert to 0-indexed
            if 0 <= page < total_pages:
                pages.append(page)
    return sorted(set(pages))


def build_pdf_content_block(
    path: Path,
    *,
    cache_control: bool = False,
) -> dict:
    """Build a Claude API content block for a PDF file."""
    block: dict = {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": encode_pdf_to_base64(path),
        },
    }
    if cache_control:
        block["cache_control"] = {"type": "ephemeral"}
    return block
