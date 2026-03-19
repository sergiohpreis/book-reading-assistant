# Reference Library Management

## Purpose

Define the reference library system that stores and manages technique PDFs used for comparing reading notes. Provides CRUD operations for adding, removing, listing, and retrieving reference materials.

## Library Structure

### Directory Location

Default: `~/.config/book-reading-assistant/library/`

Directory is created automatically on first use if it doesn't exist.

### File Organization

- PDF files stored directly in library directory
- One metadata file per PDF (optional): `<filename>.json` containing:
  - Original filename
  - File size in bytes
  - Page count
  - Date added (ISO format)
  - Original path (for reference)

Example structure:
```
~/.config/book-reading-assistant/library/
├── fichamento_guide.pdf
├── fichamento_guide.pdf.json
├── cornell_notes.pdf
└── cornell_notes.pdf.json
```

## Interface

### add(pdf_paths: List[str]) -> List[Dict]

Add one or more PDFs to the library.

**Input**:
- `pdf_paths`: List of absolute or relative paths to PDF files

**Output**:
```python
[
    {
        "name": str,           # Filename (e.g., "fichamento_guide.pdf")
        "size": int,           # File size in bytes
        "pages": int,          # Page count
        "added": str,          # ISO timestamp
        "status": str          # "success" or "error"
    },
    ...
]
```

**Behavior**:
1. Validate each file exists and is readable
2. Validate each file is a valid PDF
3. Copy file to library directory
4. Create metadata JSON file
5. Return status for each file

**Edge Cases**:
- Duplicate filename: Overwrite existing file and metadata
- Invalid PDF: Skip file, report error, continue with others
- Permission denied: Report error for that file
- Library directory doesn't exist: Create directory automatically

---

### remove(name: str) -> Dict

Remove a PDF from the library.

**Input**:
- `name`: Filename of PDF to remove (e.g., "fichamento_guide.pdf")

**Output**:
```python
{
    "name": str,        # Filename removed
    "status": str,      # "success" or "error"
    "message": str      # Confirmation or error details
}
```

**Behavior**:
1. Verify file exists in library
2. Delete PDF file
3. Delete metadata JSON file if exists
4. Return confirmation

**Edge Cases**:
- File not found: Return clear error message
- Metadata file missing: Delete PDF anyway
- Permission denied: Report error clearly
- Last reference PDF: Allow deletion (validation happens in analyzer)

---

### list() -> List[Dict]

List all PDFs currently in the library.

**Input**: None

**Output**:
```python
[
    {
        "name": str,           # Filename
        "size": int,           # File size in bytes
        "size_display": str,   # Human-readable (e.g., "2.3 MB")
        "pages": int,          # Page count
        "added": str,          # ISO timestamp
        "added_display": str   # Human-readable date
    },
    ...
]
```

Sorted alphabetically by filename.

**Behavior**:
1. Scan library directory for PDF files
2. Read metadata from JSON files
3. Get file stats (size) and page count from PDFs
4. Format data for display
5. Return list sorted by filename

**Edge Cases**:
- Empty library: Return empty list
- Library directory missing: Create it, return empty list
- Orphaned PDFs (no metadata): Get page count on-the-fly
- Invalid PDFs in directory: Skip, report warning

---

### get_all() -> List[Path]

Retrieve Path objects for all library PDFs.

**Input**: None

**Output**: List of `pathlib.Path` objects pointing to PDF files in library

**Behavior**:
1. Scan library directory for `.pdf` files
2. Return sorted list of Path objects
3. Paths are absolute

**Edge Cases**:
- Empty library: Return empty list
- Library directory missing: Create it, return empty list

---

## Metadata Management

### Metadata File Format

Each PDF has optional `<filename>.json` metadata:

```json
{
    "filename": "fichamento_guide.pdf",
    "size_bytes": 2400000,
    "pages": 45,
    "added": "2026-03-01T14:30:00Z",
    "original_path": "/home/user/downloads/fichamento_guide.pdf"
}
```

### Metadata Creation

- Created automatically when PDF is added
- Updated when PDF is overwritten
- Stores original path for user reference

### Metadata Caching

- Metadata loaded into memory on first `list()` call
- Cache invalidated after `add()` or `remove()` operations
- Allows faster repeated list operations

## File Operations

### Copy Semantics

- Source file remains unchanged
- Destination is new independent copy in library
- Large files should be copied efficiently (not memory-mapped)

### Deletion Semantics

- Both PDF and metadata JSON removed
- Empty library directory is not removed (normal state)
- No backup or recovery after deletion

### Permissions

- Library directory: rwx for owner
- PDF files: rw for owner
- Metadata files: rw for owner

## Error Handling

All operations provide clear error messages:

- **File not found**: "PDF file not found: <path>"
- **Invalid PDF**: "File is not a valid PDF: <path>"
- **Permission denied**: "Permission denied accessing: <path>"
- **Disk full**: "Not enough disk space to add PDF"
- **Invalid filename**: "Filename contains invalid characters"

## Acceptance Criteria

- [x] PDFs added to library are accessible in subsequent analyze commands
- [x] Metadata accurately reflects file contents (pages, size)
- [x] Duplicate filenames overwrite existing files with confirmation
- [x] Library directory created automatically if missing
- [x] List operation returns accurate, sorted results
- [x] get_all() returns list usable by analyzer
- [x] Remove operation completely cleans up files
- [x] Large PDFs handled efficiently (no memory issues)
- [x] All error cases handled gracefully with helpful messages
- [x] Metadata persists between CLI invocations
