"""Reference library management for technique PDFs."""

import shutil
from dataclasses import dataclass
from pathlib import Path

from book_reading_assistant.config import get_settings
from book_reading_assistant.pdf_utils import get_page_count


@dataclass
class LibraryEntry:
    """Metadata for a PDF in the library."""

    name: str
    path: Path
    size_bytes: int
    pages: int


def _get_library_dir() -> Path:
    """Get the library directory from settings."""
    return get_settings().get_library_path()


def add_pdfs(pdf_paths: list[Path], library_dir: Path | None = None) -> list[str]:
    """Copy PDF files to the library. Returns list of added file names."""
    lib = library_dir or _get_library_dir()
    added = []
    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        if not pdf_path.suffix.lower() == ".pdf":
            raise ValueError(f"Not a PDF file: {pdf_path}")
        dest = lib / pdf_path.name
        shutil.copy2(pdf_path, dest)
        added.append(pdf_path.name)
    return added


def remove_pdf(name: str, library_dir: Path | None = None) -> bool:
    """Remove a PDF from the library by name. Returns True if removed."""
    lib = library_dir or _get_library_dir()
    path = lib / name
    if not path.exists():
        # Try with .pdf extension
        path = lib / f"{name}.pdf"
    if path.exists():
        path.unlink()
        return True
    return False


def list_pdfs(library_dir: Path | None = None) -> list[LibraryEntry]:
    """List all PDFs in the library with metadata."""
    lib = library_dir or _get_library_dir()
    if not lib.exists():
        return []

    entries = []
    for pdf_path in sorted(lib.glob("*.pdf")):
        try:
            pages = get_page_count(pdf_path)
        except Exception:
            pages = 0
        entries.append(
            LibraryEntry(
                name=pdf_path.name,
                path=pdf_path,
                size_bytes=pdf_path.stat().st_size,
                pages=pages,
            )
        )
    return entries


def get_all_pdfs(library_dir: Path | None = None) -> list[Path]:
    """Return paths to all PDFs in the library."""
    lib = library_dir or _get_library_dir()
    if not lib.exists():
        return []
    return sorted(lib.glob("*.pdf"))
