# CLI Commands and Arguments

## Purpose

Define the command-line interface for the Book Reading Assistant, providing intuitive commands for analyzing notes, managing the reference library, and configuring the tool.

## Entry Point

The CLI is installed as a command-line executable named `notes` via Python entry point defined in `pyproject.toml`:

```toml
[project.scripts]
notes = "book_reading_assistant.cli:main"
```

Usage: `notes <COMMAND> [OPTIONS]`

## Commands

### analyze

Analyze reading notes against reference techniques.

**Usage**: `notes analyze <BOOK.pdf> <NOTES.md> [OPTIONS]`

**Arguments**:
- `BOOK.pdf` (required): Path to the book PDF file to analyze
- `NOTES.md` (required): Path to the reading notes file (Markdown format)

**Options**:
- `--output-dir TEXT`: Directory to save analysis results. Default: `./output`
- `--model TEXT`: Claude model to use. Default: `claude-sonnet-4-20250514`
- `--pages TEXT`: Page range(s) to analyze from the book. Format: `1-50,100-150`. If not provided, all pages analyzed.
- `--no-save`: Display results only, do not save to file. Default: False (saves results)

**Returns**: Analysis result rendered in terminal; optionally saved to file

**Examples**:
```bash
notes analyze chapter1.pdf my_notes.md
notes analyze book.pdf notes.md --pages 1-50 --model claude-3-5-sonnet-20241022
notes analyze book.pdf notes.md --output-dir ./analyses --no-save
```

**Exit Codes**:
- 0: Success
- 1: File not found or invalid input
- 2: API error
- 3: Configuration error

---

### library add

Add one or more technique PDFs to the reference library.

**Usage**: `notes library add <PDF> [PDF ...] [OPTIONS]`

**Arguments**:
- `PDF` (required, repeatable): Path(s) to PDF file(s) to add to library

**Options**: None

**Returns**: Confirmation of files added with library metadata

**Examples**:
```bash
notes library add fichamento_guide.pdf
notes library add technique1.pdf technique2.pdf technique3.pdf
notes library add /path/to/reference.pdf
```

**Exit Codes**:
- 0: Success
- 1: File not found or invalid PDF
- 2: Library error (permissions, storage)

---

### library remove

Remove a technique PDF from the reference library.

**Usage**: `notes library remove <NAME> [OPTIONS]`

**Arguments**:
- `NAME` (required): Name of the PDF file to remove (without path)

**Options**: None

**Returns**: Confirmation of file removed

**Examples**:
```bash
notes library remove fichamento_guide.pdf
```

**Exit Codes**:
- 0: Success
- 1: File not found in library
- 2: Permission denied

---

### library list

List all reference PDFs in the library.

**Usage**: `notes library list [OPTIONS]`

**Options**: None

**Returns**: Table showing filename, size, page count, and metadata

**Example Output**:
```
Reference Library Contents
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name                          Size      Pages  Added
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
fichamento_guide.pdf          2.3 MB    45     2026-03-01
cornell_notes.pdf             1.8 MB    32     2026-02-15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Exit Codes**:
- 0: Success
- 1: Library directory not found or empty

---

### config show

Display current configuration.

**Usage**: `notes config show [OPTIONS]`

**Options**: None

**Returns**: Current settings displayed in formatted table

**Example Output**:
```
Current Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setting         Value
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Key         Set (*****)
Model           claude-sonnet-4-20250514
Output Dir      ./output
Library Dir     ~/.config/book-reading-assistant/library/
Max Tokens      200000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Exit Codes**:
- 0: Success
- 1: Configuration not found

---

### config set

Update a configuration value.

**Usage**: `notes config set <KEY> <VALUE> [OPTIONS]`

**Arguments**:
- `KEY` (required): Configuration key (e.g., `model`, `output_dir`, `max_tokens`)
- `VALUE` (required): New value for the setting

**Options**: None

**Returns**: Confirmation of updated setting

**Valid Keys**:
- `model`: Claude model identifier
- `output_dir`: Directory path for saving results
- `library_dir`: Directory path for reference PDFs
- `max_tokens`: Maximum tokens per API call

**Examples**:
```bash
notes config set model claude-opus-4-1-20250805
notes config set output_dir /home/user/analyses
notes config set max_tokens 150000
```

**Exit Codes**:
- 0: Success
- 1: Invalid key
- 2: Invalid value format
- 3: Permission denied writing config

---

## Global Options

All commands support:
- `--help`: Show command help
- `--version`: Show tool version
- `--debug`: Enable debug logging

**Example**: `notes --version` or `notes analyze --help`

## Error Handling

Commands provide clear error messages for:
- Missing required arguments
- Invalid file paths
- Malformed input (invalid PDF, corrupted Markdown)
- API errors (rate limits, authentication failures)
- Configuration errors (missing API key, invalid settings)
- Storage issues (permissions, disk space)

All errors include suggestions for resolution when applicable.
