"""Prompt construction for Claude API calls."""

from pathlib import Path

from book_reading_assistant.pdf_utils import (
    build_pdf_content_block,
    extract_text,
    get_page_count,
    parse_page_ranges,
)

SYSTEM_PROMPT = (
    "You are an expert reading analyst specializing in "
    "fichamento techniques (systematic note-taking methods "
    "for academic and deep reading). "
    "You have been provided with:\n\n"
    "1. **Reference PDFs**: Books or guides on fichamento "
    "and reading note techniques\n"
    "2. **A book PDF**: The book the user has been reading\n"
    "3. **Reading notes**: The user's notes on that book\n\n"
    "Your task is to analyze the user's reading notes by:\n\n"
    "- Evaluating the quality and depth of the notes based "
    "on fichamento best practices from the references\n"
    "- Identifying which techniques from the references "
    "are being applied well\n"
    "- Pointing out areas where the notes could be improved\n"
    "- Suggesting specific techniques from the references "
    "that could enhance the note-taking\n"
    "- Assessing comprehension coverage: what key themes or "
    "arguments from the book may be missing\n\n"
    "Structure your analysis clearly with sections. "
    "Be specific — reference particular passages from the "
    "notes and techniques from the reference materials. "
    "Be constructive and encouraging while being thorough.\n\n"
    "Respond in the same language as the reading notes."
)


def build_system_prompt() -> str:
    """Return the system prompt for analysis."""
    return SYSTEM_PROMPT


def _parse_ref_pages(ref_pages: str) -> dict[str, str]:
    """Parse ref-pages spec into a mapping of filename to page range.

    Format: "file.pdf:1-30" or "file.pdf:1-30,50-60;other.pdf:10-50"
    Multiple files separated by ";", page ranges by ",".
    """
    result: dict[str, str] = {}
    for entry in ref_pages.split(";"):
        entry = entry.strip()
        if ":" not in entry:
            continue
        # Split on first colon only (filenames may not contain ":")
        name, page_spec = entry.split(":", 1)
        name = name.strip()
        page_spec = page_spec.strip()
        if name and page_spec:
            result[name] = page_spec
    return result


def build_user_content(
    ref_pdfs: list[Path],
    book_pdf: Path,
    notes_text: str,
    *,
    pages: str | None = None,
    ref_pages: str | None = None,
) -> list[dict]:
    """Build the user message content blocks for the Claude API.

    Order: reference PDFs → book PDF → notes text.
    The last reference PDF gets cache_control for prompt caching.
    """
    content: list[dict] = []

    # Reference PDFs with cache_control on the last one
    ref_page_map = _parse_ref_pages(ref_pages) if ref_pages else {}

    for i, ref_path in enumerate(ref_pdfs):
        is_last_ref = i == len(ref_pdfs) - 1
        page_spec = ref_page_map.get(ref_path.name)

        if page_spec:
            total = get_page_count(ref_path)
            page_list = parse_page_ranges(page_spec, total)
            text = extract_text(ref_path, page_list)
            block: dict = {
                "type": "text",
                "text": (
                    f"## Reference: {ref_path.name} "
                    f"(pages: {page_spec})\n\n{text}"
                ),
            }
            if is_last_ref:
                block["cache_control"] = {"type": "ephemeral"}
            content.append(block)
        else:
            content.append(
                build_pdf_content_block(
                    ref_path, cache_control=is_last_ref,
                )
            )

    # Book PDF (with optional page filtering via text extraction)
    if pages:
        total_pages = get_page_count(book_pdf)
        page_list = parse_page_ranges(pages, total_pages)
        text = extract_text(book_pdf, page_list)
        content.append({
            "type": "text",
            "text": f"## Book content (pages: {pages})\n\n{text}",
        })
    else:
        content.append(build_pdf_content_block(book_pdf))

    # Reading notes
    content.append({
        "type": "text",
        "text": f"## Reading Notes\n\n{notes_text}",
    })

    return content
