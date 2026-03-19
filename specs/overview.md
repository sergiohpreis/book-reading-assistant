# Book Reading Assistant - System Overview

## Purpose

The Book Reading Assistant is a CLI tool that analyzes book reading notes against established fichamento techniques using Claude API. It helps readers improve their note-taking by comparing their notes against reference materials that demonstrate proper note-taking methodologies.

## System Architecture

### Components

- **CLI Interface**: Command-line tool named `notes`, installed via Python entry point
- **Analyzer Engine**: Core logic for comparing notes against reference techniques
- **Reference Library**: Local storage of technique PDFs at `~/.config/book-reading-assistant/library/`
- **Claude API Integration**: Uses Anthropic Claude API with prompt caching for efficient processing
- **Configuration System**: Manages settings via environment variables and configuration files

### Technology Stack

- **Language**: Python 3.10+
- **CLI Framework**: Click or similar
- **PDF Processing**: pypdf for reading and extracting content
- **AI Provider**: Anthropic Claude API
- **Configuration**: pydantic-settings
- **Output Formatting**: rich for terminal rendering
- **Caching**: Claude prompt caching with ephemeral cache control

## Key Workflows

### Analyze Reading Notes

1. User invokes `notes analyze <BOOK.pdf> <NOTES.md>`
2. System loads reference PDFs from library
3. System loads book PDF and reading notes
4. Estimates token usage for API call
5. Validates against token budget (max 200,000 tokens)
6. Builds Claude message with cache-controlled reference PDFs
7. Calls Claude API with analysis instructions
8. Displays results in terminal or saves to file

### Manage Reference Library

1. User adds technique PDFs: `notes library add <PDF> [PDF...]`
2. Files copied to library directory with metadata tracking
3. User can list, remove, or view library contents
4. Library provides PDFs to analysis workflow

## Cache Strategy

- Reference PDFs use ephemeral cache control on the last reference PDF in the message
- Caching reduces API costs and improves performance for repeated analyses
- Cache is maintained across multiple analysis runs

## Configuration

Settings loaded from:
1. Environment variables (ANTHROPIC_API_KEY, MODEL, OUTPUT_DIR, LIBRARY_DIR, MAX_TOKENS)
2. `.env` file in project root
3. `~/.config/book-reading-assistant/config.json` (optional)

Default values:
- Model: claude-sonnet-4-20250514
- Output directory: ./output
- Library directory: ~/.config/book-reading-assistant/library/
- Max tokens: 200,000

## Success Metrics

- Users can analyze notes in seconds
- Analysis provides actionable feedback on note quality
- Reference PDFs reduce analysis latency via caching
- Configuration is flexible and environment-aware
- Outputs are readable and saved for future reference
