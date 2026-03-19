# Configuration Management

## Purpose

Define configuration system for the Book Reading Assistant. Manages settings via environment variables, .env files, and optional configuration files with sensible defaults.

## Configuration Architecture

### Settings Source Priority

Configuration is loaded in this priority order (highest to lowest):

1. **Environment variables**: ANTHROPIC_API_KEY, MODEL, OUTPUT_DIR, LIBRARY_DIR, MAX_TOKENS
2. **.env file**: Project root `.env` file (loaded by python-dotenv)
3. **Config file**: `~/.config/book-reading-assistant/config.json` (optional)
4. **Defaults**: Built-in default values

Settings at higher priority override those below.

### Implementation

Using `pydantic-settings` for type-safe configuration:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """Application configuration with pydantic-settings."""

    # API Configuration
    anthropic_api_key: str  # No default - required
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 200000

    # Storage Configuration
    output_dir: str = "./output"
    library_dir: str = "~/.config/book-reading-assistant/library/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra env vars
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Expand home directory paths
        self.output_dir = str(Path(self.output_dir).expanduser())
        self.library_dir = str(Path(self.library_dir).expanduser())
```

## Configuration Settings

### ANTHROPIC_API_KEY

**Type**: String

**Required**: Yes

**Description**: API key for Anthropic Claude API authentication

**Sources**:
- Environment variable: `ANTHROPIC_API_KEY`
- .env file: `ANTHROPIC_API_KEY=sk-...`

**Validation**:
- Must not be empty
- Should start with "sk-" (format check)

**Error Handling**:
```
Error: ANTHROPIC_API_KEY not set

Set your API key in one of:
  1. Environment variable: export ANTHROPIC_API_KEY="sk-..."
  2. .env file: ANTHROPIC_API_KEY=sk-...
  3. Config file: ~/.config/book-reading-assistant/config.json

Get your key at: https://console.anthropic.com/
```

---

### model

**Type**: String

**Default**: `claude-sonnet-4-20250514`

**Description**: Claude model to use for analysis

**Sources**:
- Environment variable: `MODEL`
- .env file: `MODEL=claude-opus-4-1-20250805`
- CLI flag: `--model` (highest priority)

**Valid Values**:
- `claude-opus-4-1-20250805`
- `claude-sonnet-4-20250514`
- `claude-haiku-4-5-20251001`
- Other Claude models as they become available

**Validation**:
- Model name must contain "claude"
- No empty strings

**Example**:
```bash
# Via environment
export MODEL=claude-opus-4-1-20250805

# Via .env
MODEL=claude-opus-4-1-20250805

# Via CLI
notes analyze book.pdf notes.md --model claude-opus-4-1-20250805
```

---

### output_dir

**Type**: String (path)

**Default**: `./output` (relative to current working directory)

**Description**: Directory where analysis results are saved

**Sources**:
- Environment variable: `OUTPUT_DIR`
- .env file: `OUTPUT_DIR=/home/user/analyses`
- CLI flag: `--output-dir` (highest priority)

**Behavior**:
- Expands `~` and `$HOME` to home directory
- Created automatically if doesn't exist
- Parent directories created as needed
- Relative paths interpreted from CWD

**Example Paths**:
```bash
./output                                     # Relative
~/analyses                                   # Home-relative
/home/user/book-analyses                     # Absolute
/Volumes/external/backup                     # External drive
```

**Permissions**:
- Directory created with rwx for owner
- Write permission required

---

### library_dir

**Type**: String (path)

**Default**: `~/.config/book-reading-assistant/library/`

**Description**: Directory storing reference PDF files

**Sources**:
- Environment variable: `LIBRARY_DIR`
- .env file: `LIBRARY_DIR=~/.local/share/book-reading-assistant/library`

**Behavior**:
- Expands `~` and `$HOME` to home directory
- Created automatically on first use
- Standard locations follow XDG Base Directory spec (optional)
- Must be readable and writable

**XDG Compliant Alternatives**:
```bash
~/.config/book-reading-assistant/library/     # XDG_CONFIG_HOME
~/.local/share/book-reading-assistant/        # XDG_DATA_HOME
```

**Example**:
```bash
# Export to use alternate location
export LIBRARY_DIR=~/.local/share/reading-references
```

---

### max_tokens

**Type**: Integer

**Default**: `200000`

**Description**: Maximum total tokens allowed per API call

**Sources**:
- Environment variable: `MAX_TOKENS`
- .env file: `MAX_TOKENS=150000`

**Constraints**:
- Must be >= 4096 (minimum for output)
- Must be <= 200000 (Claude's practical limit)

**Behavior**:
- Analyzer checks estimated tokens against this limit
- If exceeded, provides helpful error with suggestions
- Not enforced by API call (soft limit)

**Example**:
```bash
# Use more conservative limit
export MAX_TOKENS=100000

# Use aggressive limit (for powerful analysis)
export MAX_TOKENS=200000
```

---

## Configuration Files

### .env File

**Location**: Project root (`.env`)

**Format**: Key=Value, one per line

**Example**:
```ini
ANTHROPIC_API_KEY=sk-ant-v8...
MODEL=claude-sonnet-4-20250514
OUTPUT_DIR=~/analyses
LIBRARY_DIR=~/.config/book-reading-assistant/library/
MAX_TOKENS=200000
```

**Loading**:
- Automatically loaded by pydantic-settings
- Only used if file exists
- Environment variables override

**Security**:
- Add to `.gitignore` to prevent committing API keys
- Permissions: rw for owner only (600)

---

### Config File

**Location**: `~/.config/book-reading-assistant/config.json`

**Format**: JSON

**Example**:
```json
{
    "model": "claude-opus-4-1-20250805",
    "output_dir": "/home/user/analyses",
    "library_dir": "/home/user/.local/share/references",
    "max_tokens": 150000
}
```

**Note**: This is optional. Most users configure via environment variables and .env.

---

## Configuration Commands

### notes config show

Display current configuration.

**Output**:
```
Current Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setting         Value
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Key         Set (*****)
Model           claude-sonnet-4-20250514
Output Dir      /home/user/analyses
Library Dir     /home/user/.config/book-reading-assistant/library/
Max Tokens      200000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Behavior**:
- Shows source for each setting (env var, .env, config file, or default)
- Masks API key for security
- Shows expanded paths (~ expanded to home)

---

### notes config set

Update a configuration value.

**Usage**: `notes config set <KEY> <VALUE>`

**Behavior**:
1. Validates key name
2. Validates value format
3. Saves to config file
4. Shows confirmation

**Example**:
```bash
notes config set model claude-opus-4-1-20250805
notes config set max_tokens 150000
```

**Stored Location**:
- Saves to `~/.config/book-reading-assistant/config.json`
- Creates file and directories if needed
- Preserves other settings in file

---

## Environment Variable Reference

**All settings accept environment variable equivalents**:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export MODEL="claude-sonnet-4-20250514"
export OUTPUT_DIR="~/analyses"
export LIBRARY_DIR="~/.config/book-reading-assistant/library/"
export MAX_TOKENS="200000"
```

**Case Sensitivity**: Variables are case-insensitive (automatically converted to lowercase)

---

## Default Values Summary

| Setting | Default | Required |
|---------|---------|----------|
| ANTHROPIC_API_KEY | - | Yes |
| model | claude-sonnet-4-20250514 | No |
| output_dir | ./output | No |
| library_dir | ~/.config/book-reading-assistant/library/ | No |
| max_tokens | 200000 | No |

---

## Validation and Error Handling

### Missing Required Settings

```
Error: ANTHROPIC_API_KEY not configured

Please set ANTHROPIC_API_KEY in one of:
  - Environment variable: export ANTHROPIC_API_KEY="sk-..."
  - .env file in current directory
  - ~/.config/book-reading-assistant/config.json
```

### Invalid Values

```
Error: Invalid model value

Must be a valid Claude model identifier.
Examples: claude-opus-4-1-20250805, claude-sonnet-4-20250514

Current value: invalid-model-name
```

### Directory Access Issues

```
Error: Cannot write to output directory

Directory: /home/user/analyses
Issue: Permission denied

Solutions:
  1. Change output_dir to a writable location
  2. Check directory permissions: chmod u+w /home/user/analyses
  3. Use default: export OUTPUT_DIR="./output"
```

## Acceptance Criteria

- [x] Configuration loads from all documented sources
- [x] Priority order enforced (env > .env > config file > defaults)
- [x] ANTHROPIC_API_KEY required with helpful error message
- [x] All settings validated with type checking
- [x] Home directory paths expanded correctly
- [x] Output and library directories created if missing
- [x] config show displays all settings clearly
- [x] config set updates values and persists to file
- [x] API key masked in config show for security
- [x] Default values sensible and documented
- [x] Works in different environments (dev, CI/CD, production)
