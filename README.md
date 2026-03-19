# Book Reading Assistant

CLI tool that reviews book reading notes against fichamento techniques using Claude AI.

## How it works

You provide:

1. **Reference PDFs** — one or more books/guides on fichamento techniques (added to the library or pointed to via `--library-dir`)
2. **A book PDF** — the book you've been reading
3. **Your reading notes** — a Markdown file with your notes on the book

The tool sends all of these to Claude, which analyzes your notes based on the fichamento techniques from the references.

> All reference PDFs in the library are used in every analysis. If your references are large, use `--ref-pages` to select specific pages.

## Requirements

- An [Anthropic API key](https://console.anthropic.com/)
- **Option A (local):** Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- **Option B (Docker):** Docker and Docker Compose

## Setup

```bash
# Configure your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage with Docker

No Python or uv installation needed — just Docker.

```bash
# Build the image
docker compose build

# Add one or more reference PDFs (place them in data/)
docker compose run --rm notes library add /data/techniques.pdf
docker compose run --rm notes library add /data/another-reference.pdf

# Analyze your reading notes
docker compose run --rm notes analyze /data/book.pdf /data/my-notes.md
```

You can also skip the library and point directly to a folder with your reference PDFs:

```bash
docker compose run --rm notes analyze /data/book.pdf /data/my-notes.md --library-dir /data/refs/
```

Place your PDFs and notes in the `data/` directory — it's mounted as `/data` inside the container.

## Usage with uv (local)

```bash
# Install dependencies
uv sync

# Add one or more reference PDFs (fichamento techniques)
uv run notes library add path/to/techniques.pdf path/to/another.pdf

# Analyze your reading notes
uv run notes analyze book.pdf my-notes.md

# Or point to a folder with references instead of using the library
uv run notes analyze book.pdf my-notes.md --library-dir ./refs/
```

For large PDFs, select page ranges:

```bash
uv run notes analyze book.pdf my-notes.md --pages 1-50 --ref-pages "techniques.pdf:1-30"
```

## Options

| Flag | Description |
|------|-------------|
| `--output-dir` | Custom output directory (default: `./output`) |
| `--model` | Claude model to use |
| `--pages` | Page range for the book (e.g. `1-50,100-150`) |
| `--ref-pages` | Page ranges per reference (e.g. `"file.pdf:1-30;other.pdf:10-50"`) |
| `--library-dir` | Reference PDFs directory (overrides config) |
| `--no-save` | Don't save output to file |

## Other commands

```bash
notes library list                            # List reference PDFs
notes library remove techniques.pdf           # Remove a reference PDF
notes config show                             # Show current configuration
notes config set model claude-opus-4-20250514 # Update a setting
```

## Development

```bash
uv sync --extra dev
uv run pytest          # Run tests
uv run ruff check      # Lint
```
