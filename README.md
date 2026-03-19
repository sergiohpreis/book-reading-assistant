# Book Reading Assistant

CLI tool that reviews book reading notes against fichamento techniques using Claude AI.

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

# Add reference PDFs (place them in data/)
docker compose run --rm notes library add /data/techniques.pdf

# Analyze your reading notes
docker compose run --rm notes analyze /data/book.pdf /data/my-notes.md
```

Place your PDFs and notes in the `data/` directory — it's mounted as `/data` inside the container.

## Usage with uv (local)

```bash
# Install dependencies
uv sync

# Add reference PDFs (fichamento techniques)
uv run notes library add path/to/techniques.pdf

# Analyze your reading notes
uv run notes analyze book.pdf my-notes.md
```

For large PDFs, select a page range:

```bash
uv run notes analyze book.pdf my-notes.md --pages 1-50,100-150
```

## Options

| Flag | Description |
|------|-------------|
| `--output-dir` | Custom output directory (default: `./output`) |
| `--model` | Claude model to use |
| `--pages` | Page range (e.g. `1-50,100-150`) |
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
