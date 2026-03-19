"""Core analysis orchestration."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import anthropic

from book_reading_assistant.config import Settings, get_settings
from book_reading_assistant.library import get_all_pdfs
from book_reading_assistant.pdf_utils import estimate_tokens
from book_reading_assistant.prompts import build_system_prompt, build_user_content


@dataclass
class AnalysisResult:
    """Result of a reading notes analysis."""

    content: str
    model: str
    book_name: str
    notes_name: str
    references: list[str]
    timestamp: datetime = field(default_factory=datetime.now)
    input_tokens: int = 0
    output_tokens: int = 0


class TokenBudgetError(Exception):
    """Raised when estimated tokens exceed the budget."""

    def __init__(self, estimated: int, budget: int):
        self.estimated = estimated
        self.budget = budget
        super().__init__(
            f"Estimated tokens ({estimated:,}) exceed budget ({budget:,}). "
            f"Use --pages to select a page range or reduce reference PDFs."
        )


def estimate_total_tokens(
    ref_pdfs: list[Path],
    book_pdf: Path,
    notes_text: str,
) -> int:
    """Estimate total tokens for all inputs."""
    total = sum(estimate_tokens(pdf) for pdf in ref_pdfs)
    total += estimate_tokens(book_pdf)
    # Rough text token estimate: ~4 chars per token
    total += len(notes_text) // 4
    return total


def analyze(
    book_pdf: Path,
    notes_path: Path,
    *,
    settings: Settings | None = None,
    pages: str | None = None,
    model: str | None = None,
    library_dir: str | None = None,
) -> AnalysisResult:
    """Run the full analysis pipeline."""
    settings = settings or get_settings()
    model = model or settings.model

    # Load inputs
    lib_path = Path(library_dir) if library_dir else Path(settings.library_dir)
    ref_pdfs = get_all_pdfs(lib_path)
    if not ref_pdfs:
        raise ValueError(
            "No reference PDFs in library. Add some with: notes library add <PDF>"
        )

    notes_text = notes_path.read_text(encoding="utf-8")
    if not notes_text.strip():
        raise ValueError(f"Notes file is empty: {notes_path}")

    # Token estimation (skip if using --pages since that reduces tokens)
    if not pages:
        estimated = estimate_total_tokens(ref_pdfs, book_pdf, notes_text)
        if estimated > settings.max_tokens:
            raise TokenBudgetError(estimated, settings.max_tokens)

    # Build API request
    system_prompt = build_system_prompt()
    user_content = build_user_content(ref_pdfs, book_pdf, notes_text, pages=pages)

    # Call Claude API
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=model,
        max_tokens=16_384,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    # Extract result
    content = ""
    for block in response.content:
        if block.type == "text":
            content += block.text

    return AnalysisResult(
        content=content,
        model=model,
        book_name=book_pdf.stem,
        notes_name=notes_path.name,
        references=[p.name for p in ref_pdfs],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
