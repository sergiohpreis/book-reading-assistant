"""Output formatting: terminal display and file saving."""

from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from book_reading_assistant.analyzer import AnalysisResult

console = Console()


def display_analysis(result: AnalysisResult) -> None:
    """Render analysis result in the terminal using Rich."""
    # Metadata panel
    meta_lines = [
        f"Book: {result.book_name}",
        f"Notes: {result.notes_name}",
        f"Model: {result.model}",
        f"Date: {result.timestamp.strftime('%Y-%m-%d %H:%M')}",
        f"References: {', '.join(result.references)}",
        f"Tokens: {result.input_tokens:,} in / {result.output_tokens:,} out",
    ]
    console.print(Panel("\n".join(meta_lines), title="Analysis Metadata"))
    console.print()

    # Analysis content
    console.print(Markdown(result.content))


def save_analysis(result: AnalysisResult, output_dir: Path) -> Path:
    """Save analysis result as a Markdown file with YAML front-matter."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = result.timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{result.book_name}_analysis_{timestamp_str}.md"
    output_path = output_dir / filename

    refs_yaml = "\n".join(f"  - {r}" for r in result.references)

    content = f"""---
book: {result.book_name}
notes: {result.notes_name}
model: {result.model}
date: {result.timestamp.isoformat()}
references:
{refs_yaml}
---

{result.content}
"""
    output_path.write_text(content, encoding="utf-8")
    return output_path
