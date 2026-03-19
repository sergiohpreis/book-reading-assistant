# Output Formatting and Display

## Purpose

Define how analysis results are displayed to users and saved to files. Provides functions for terminal rendering with rich formatting and file persistence with metadata.

## Display Output

### display_analysis(result: Dict, metadata: Dict) -> None

Render analysis result in the terminal with rich formatting.

**Input**:
- `result`: Analysis result dict from analyzer with keys:
  - `content`: Claude's analysis text
  - `model`: Model used
  - `usage`: Token usage dict
  - `timestamp`: Datetime of analysis

- `metadata`: Context dict with keys:
  - `book_file`: Path to book PDF analyzed
  - `notes_file`: Path to notes file analyzed
  - `pages_analyzed`: Page range or "all"
  - `references_used`: List of reference PDF names

**Behavior**:
1. Create metadata panel with book, notes, model, timestamp
2. Render analysis content as Markdown with syntax highlighting
3. Display token usage statistics
4. Render to terminal using rich library

**Example Output**:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Analysis Metadata                                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Book File:     chapter1.pdf                            ┃
┃ Notes File:    my_notes.md                             ┃
┃ Pages:         1-50                                    ┃
┃ Model:         claude-sonnet-4-20250514                ┃
┃ Timestamp:     2026-03-19 14:30:45 UTC                 ┃
┃ References:    fichamento_guide.pdf                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

## Analysis Summary
Your notes demonstrate strong organizational structure with clear section
headings and logical flow. The main concepts are well captured, though some
supporting details could be more specific.

## Detailed Feedback by Category

### 1. Structure and Organization
[... full analysis content ...]

[... more sections ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Token Usage:     6,250 input | 1,840 output | 0 cached
```

**Implementation**:

```python
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.console import Console
from datetime import datetime

def display_analysis(result: Dict, metadata: Dict) -> None:
    """
    Display analysis result in terminal with rich formatting.

    Args:
        result: Analysis result from analyzer
        metadata: Metadata dict with context
    """
    console = Console()

    # Create metadata panel
    metadata_text = (
        f"Book File:     {metadata['book_file']}\n"
        f"Notes File:    {metadata['notes_file']}\n"
        f"Pages:         {metadata['pages_analyzed']}\n"
        f"Model:         {result['model']}\n"
        f"Timestamp:     {result['timestamp']}\n"
        f"References:    {', '.join(metadata['references_used']) or 'None'}"
    )

    panel = Panel(
        metadata_text,
        title="Analysis Metadata",
        expand=False
    )
    console.print(panel)
    console.print()

    # Display analysis content as Markdown
    markdown = Markdown(result['content'])
    console.print(markdown)
    console.print()

    # Display token usage
    usage = result['usage']
    usage_line = (
        f"Token Usage:     {usage['input_tokens']} input | "
        f"{usage['output_tokens']} output"
    )
    if usage.get('cache_read_input_tokens', 0) > 0:
        usage_line += f" | {usage['cache_read_input_tokens']} cached"

    console.print(usage_line)
```

## Save Output

### save_analysis(result: Dict, metadata: Dict, output_dir: str | Path) -> Path

Save analysis result to a Markdown file with YAML front-matter.

**Input**:
- `result`: Analysis result dict from analyzer
- `metadata`: Context dict with analysis details
- `output_dir`: Directory to save file to (created if doesn't exist)

**Output**: Path to saved file

**Behavior**:
1. Create output directory if it doesn't exist
2. Generate filename with timestamp
3. Create YAML front-matter with metadata
4. Write analysis content as Markdown
5. Return Path to saved file

**File Naming**:
- Format: `{book_name}_analysis_{YYYYMMDD_HHMMSS}.md`
- Example: `chapter1_analysis_20260319_143045.md`
- Book name extracted from file path, lowercase

**File Structure**:

```markdown
---
book: chapter1.pdf
notes: my_notes.md
model: claude-sonnet-4-20250514
date: 2026-03-19T14:30:45Z
pages: 1-50
references:
  - fichamento_guide.pdf
tokens:
  input: 6250
  output: 1840
  cached: 0
---

# Analysis Result

## Analysis Summary
[... analysis content ...]
```

**Implementation**:

```python
from pathlib import Path
from datetime import datetime
import yaml

def save_analysis(
    result: Dict,
    metadata: Dict,
    output_dir: str | Path
) -> Path:
    """
    Save analysis result to file with YAML front-matter.

    Args:
        result: Analysis result from analyzer
        metadata: Metadata dict with context
        output_dir: Directory to save to

    Returns:
        Path to saved file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    book_name = Path(metadata['book_file']).stem
    timestamp = result['timestamp'].strftime('%Y%m%d_%H%M%S')
    filename = f"{book_name}_analysis_{timestamp}.md"
    filepath = output_dir / filename

    # Create front-matter
    frontmatter = {
        'book': metadata['book_file'],
        'notes': metadata['notes_file'],
        'model': result['model'],
        'date': result['timestamp'].isoformat(),
        'pages': metadata['pages_analyzed'],
        'references': metadata['references_used'],
        'tokens': {
            'input': result['usage']['input_tokens'],
            'output': result['usage']['output_tokens'],
            'cached': result['usage'].get('cache_read_input_tokens', 0)
        }
    }

    # Write file
    with open(filepath, 'w') as f:
        f.write('---\n')
        f.write(yaml.dump(frontmatter, default_flow_style=False))
        f.write('---\n\n')
        f.write(result['content'])

    return filepath
```

## Output Formatting Standards

### Markdown Conventions

- Use standard Markdown headers (# ## ### etc.)
- Code blocks use triple backticks with language identifier
- Lists use proper indentation
- Links use `[text](url)` format
- Bold for emphasis: **important**
- Italics for notes: *example*

### File Encoding

- Files saved as UTF-8 with no BOM
- Line endings: LF (Unix style)
- No trailing whitespace on lines

### Directory Handling

- Output directory created automatically if missing
- Parent directories created as needed
- Permissions: rwx for owner

### File Cleanup

- Old analysis files not automatically deleted
- Users can manually manage output directory
- Consider adding `notes clean` command in future for housekeeping

## Error Handling

**Display Errors**:
- Terminal rendering errors caught, content printed as plain text fallback
- Rich library errors don't prevent output

**Save Errors**:
- Permission denied: Raise `PermissionError` with output dir path
- Disk full: Raise `IOError` with suggestion to check disk space
- Invalid path: Raise `ValueError` with path details

**Invalid Metadata**:
- Missing keys default to sensible values
- Empty references list displays as "None"
- Missing timestamp uses current time

## Performance

- Display: < 1 second for typical analysis (< 10KB content)
- Save: < 100ms for file I/O
- Both operations non-blocking for user experience

## Terminal Capabilities

- Detects color support and adjusts rendering
- Falls back to plain text if terminal doesn't support rich
- Terminal width detection for responsive layout
- Works in CI/CD environments without color codes

## Acceptance Criteria

- [x] Analysis displays in terminal with clear formatting
- [x] Metadata panel shows all relevant context
- [x] Content rendered as Markdown with proper syntax highlighting
- [x] Token usage displayed accurately
- [x] Files saved with correct naming convention
- [x] YAML front-matter includes all metadata
- [x] Files are valid Markdown with proper structure
- [x] Output directory created automatically if needed
- [x] Saved files are human-readable and parseable
- [x] Error messages guide users toward solutions
- [x] Performance meets user expectations (< 1 second)
