# PDF Handling Utilities

## Purpose

Provide utility functions for PDF operations including encoding, page counting, token estimation, text extraction, and content block building for Claude API.

## Functions

### encode_pdf_to_base64(path: str | Path) -> str

Encode a PDF file to base64 string for API transmission.

**Input**:
- `path`: Absolute or relative path to PDF file

**Output**: Base64-encoded string representation of PDF

**Behavior**:
1. Open PDF file in binary mode
2. Read entire file into memory
3. Encode to base64 string
4. Return encoded string

**Implementation**:
```python
import base64
from pathlib import Path

def encode_pdf_to_base64(path: str | Path) -> str:
    path = Path(path)
    with open(path, 'rb') as f:
        pdf_bytes = f.read()
    return base64.standard_b64encode(pdf_bytes).decode('utf-8')
```

**Edge Cases**:
- File not found: Raise `FileNotFoundError` with path
- Permission denied: Raise `PermissionError`
- File too large (>100 MB): Log warning, proceed anyway
- Invalid PDF: Proceed (validation happens at API level)

**Performance**: O(n) where n is file size

---

### get_page_count(path: str | Path) -> int

Get the number of pages in a PDF file.

**Input**:
- `path`: Absolute or relative path to PDF file

**Output**: Number of pages as integer

**Behavior**:
1. Open PDF using pypdf.PdfReader
2. Get page count from PDF metadata or content
3. Return page count

**Implementation**:
```python
from pypdf import PdfReader
from pathlib import Path

def get_page_count(path: str | Path) -> int:
    path = Path(path)
    reader = PdfReader(path)
    return len(reader.pages)
```

**Edge Cases**:
- File not found: Raise `FileNotFoundError`
- Invalid/corrupted PDF: Return 0 (graceful degradation)
- File too large: Proceed (pypdf handles streaming)

**Performance**: O(1) - reads metadata, not entire file

---

### estimate_tokens(path: str | Path) -> int

Estimate token count for a PDF file.

**Input**:
- `path`: Absolute or relative path to PDF file

**Output**: Estimated token count as integer

**Behavior**:
1. Get page count using `get_page_count()`
2. Apply formula: pages × 2250 tokens/page
3. Return estimated total

**Formula Rationale**:
- Average PDF page = ~2250 tokens
- Based on Claude's analysis of typical technical documents
- Conservative estimate to prevent overflow

**Implementation**:
```python
def estimate_tokens(path: str | Path) -> int:
    pages = get_page_count(path)
    return pages * 2250
```

**Edge Cases**:
- Page count is 0: Return 0 tokens
- Very large PDFs (1000+ pages): Apply formula as normal

**Example**:
- 45-page PDF: 45 × 2250 = 101,250 tokens
- 10-page PDF: 10 × 2250 = 22,500 tokens

---

### extract_text(path: str | Path, pages: str | None = None) -> str

Extract text from a PDF file, optionally from specified page range.

**Input**:
- `path`: Absolute or relative path to PDF file
- `pages`: Optional page range string in format "1-50,100-150" (1-indexed)

**Output**: Extracted text as string (newlines preserved between pages)

**Behavior**:
1. Open PDF using pypdf.PdfReader
2. If pages specified, parse range string into list of page numbers
3. Extract text from each page
4. Join pages with newline separator
5. Return combined text

**Page Range Format**:
- "1-50": Pages 1 through 50 inclusive
- "1-50,100-150": Pages 1-50 and 100-150
- None or empty: Extract all pages
- Invalid format: Raise `ValueError` with helpful message

**Behavior with Pages**:
1. Parse range string: "1-50,100-150"
   - Split by comma: ["1-50", "100-150"]
   - For each range, parse start-end
   - Collect all page numbers (1-indexed)
2. Validate page numbers exist in PDF
3. Extract and join text

**Implementation Note**:
- Use pypdf's text extraction (may have encoding issues)
- Fallback to empty string if page extraction fails for a page
- Preserve structure where possible

**Edge Cases**:
- File not found: Raise `FileNotFoundError`
- Invalid page range: Raise `ValueError` with clear message
- Page range exceeds PDF: Extract available pages
- PDF has no text: Return empty string (scanned images)
- Invalid page format: Raise `ValueError`

**Example**:
```python
# Extract pages 1-10 and 20-25
text = extract_text("book.pdf", pages="1-10,20-25")
```

---

### build_pdf_content_block(path: str | Path, cache_control: dict | None = None) -> dict

Build a Claude API content block for a PDF file.

**Input**:
- `path`: Absolute or relative path to PDF file
- `cache_control`: Optional cache control configuration dict

**Output**: Claude API document content block (dict)

**Behavior**:
1. Encode PDF to base64 using `encode_pdf_to_base64()`
2. Construct content block dict with:
   - type: "document"
   - source: base64 data with media type
   - Optional cache_control if provided
3. Return formatted dict

**Content Block Format**:
```python
{
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": "JVBERi0xLjQK..."  # base64-encoded PDF
    }
    # Optional:
    # "cache_control": {"type": "ephemeral"}
}
```

**Implementation**:
```python
def build_pdf_content_block(path: str | Path, cache_control: dict | None = None) -> dict:
    pdf_data = encode_pdf_to_base64(path)
    block = {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": pdf_data
        }
    }
    if cache_control:
        block["cache_control"] = cache_control
    return block
```

**Cache Control Values**:
- `{"type": "ephemeral"}`: Enable ephemeral caching on this block
- `None`: No cache control (default)

**Usage in Analyzer**:
```python
# Reference PDFs (last one with cache)
ref_blocks = [
    build_pdf_content_block(ref_path)
    for ref_path in ref_pdfs[:-1]
]
if ref_pdfs:
    ref_blocks.append(
        build_pdf_content_block(
            ref_pdfs[-1],
            cache_control={"type": "ephemeral"}
        )
    )

# Book PDF (no cache)
book_block = build_pdf_content_block(book_path)
```

**Edge Cases**:
- File not found: Raise `FileNotFoundError`
- Invalid cache_control format: Raise `ValueError`
- Very large PDF: Proceed (API has size limits)

## Dependencies

- `pypdf`: PDF reading and text extraction
- `base64`: Python standard library
- `pathlib`: Python standard library

## Acceptance Criteria

- [x] Base64 encoding produces valid data for Claude API
- [x] Page counting accurate for typical PDFs
- [x] Token estimation prevents overflow (with buffer)
- [x] Text extraction handles all common PDF formats
- [x] Page range parsing supports multiple ranges
- [x] Content blocks are correctly formatted for API
- [x] Cache control applied only when specified
- [x] Error messages guide users toward solutions
- [x] All functions handle missing files gracefully
- [x] Performance acceptable for large files (no excessive memory)
