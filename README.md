# Book Reading Assistant

CLI tool that reviews book reading notes against fichamento techniques using Claude AI.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
# Install dependencies
uv sync

# Configure your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### 1. Add reference PDFs (fichamento techniques)

```bash
uv run notes library add path/to/techniques.pdf
uv run notes library list
```

### 2. Analyze your reading notes

```bash
uv run notes analyze book.pdf my-notes.md
```

For large PDFs, select a page range:

```bash
uv run notes analyze book.pdf my-notes.md --pages 1-50,100-150
```

### Options

| Flag | Description |
|------|-------------|
| `--output-dir` | Custom output directory (default: `./output`) |
| `--model` | Claude model to use |
| `--pages` | Page range (e.g. `1-50,100-150`) |
| `--no-save` | Don't save output to file |

### Other commands

```bash
uv run notes library remove techniques.pdf  # Remove a reference PDF
uv run notes config show                    # Show current configuration
uv run notes config set model claude-opus-4-20250514  # Update a setting
```

## Docker

```bash
# Build
docker compose build

# Run
docker compose run --rm notes analyze /data/book.pdf /data/my-notes.md
```

Place your PDFs and notes in the `data/` directory — it's mounted as `/data` inside the container.

## Development

```bash
uv sync --extra dev
uv run pytest          # Run tests
uv run ruff check      # Lint
```
