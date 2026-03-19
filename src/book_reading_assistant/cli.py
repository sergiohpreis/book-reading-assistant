"""CLI entry point using Typer."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from book_reading_assistant.analyzer import TokenBudgetError, analyze
from book_reading_assistant.config import get_settings, save_config
from book_reading_assistant.library import add_pdfs, list_pdfs, remove_pdf
from book_reading_assistant.output import display_analysis, save_analysis

app = typer.Typer(
    name="notes",
    help="Book Reading Assistant — analyze reading notes using fichamento techniques.",
    no_args_is_help=True,
)
library_app = typer.Typer(
    help="Manage the reference PDF library.",
    no_args_is_help=True,
)
config_app = typer.Typer(
    help="View and update configuration.",
    no_args_is_help=True,
)

app.add_typer(library_app, name="library")
app.add_typer(config_app, name="config")

console = Console()


@app.command("analyze")
def analyze_cmd(
    book_pdf: Annotated[Path, typer.Argument(help="Path to the book PDF")],
    notes: Annotated[Path, typer.Argument(help="Path to the reading notes (.md)")],
    output_dir: Annotated[
        str | None, typer.Option("--output-dir", help="Output directory")
    ] = None,
    model: Annotated[
        str | None, typer.Option("--model", help="Claude model to use")
    ] = None,
    pages: Annotated[
        str | None,
        typer.Option("--pages", help="Page range (e.g. '1-50,100-150')"),
    ] = None,
    library_dir: Annotated[
        str | None,
        typer.Option("--library-dir", help="Reference PDFs directory"),
    ] = None,
    ref_pages: Annotated[
        str | None,
        typer.Option(
            "--ref-pages",
            help="Page ranges per reference (e.g. 'file.pdf:1-30;other.pdf:10-50')",
        ),
    ] = None,
    no_save: Annotated[
        bool, typer.Option("--no-save", help="Don't save output to file")
    ] = False,
) -> None:
    """Analyze reading notes against reference techniques."""
    if not book_pdf.exists():
        console.print(f"[red]Book PDF not found: {book_pdf}[/red]")
        raise typer.Exit(1)
    if not notes.exists():
        console.print(f"[red]Notes file not found: {notes}[/red]")
        raise typer.Exit(1)

    settings = get_settings()

    if not settings.anthropic_api_key:
        console.print(
            "[red]ANTHROPIC_API_KEY not set. "
            "Set it in .env or environment variables.[/red]"
        )
        raise typer.Exit(1)

    try:
        with console.status("Analyzing reading notes..."):
            result = analyze(
                book_pdf,
                notes,
                settings=settings,
                pages=pages,
                model=model,
                library_dir=library_dir,
                ref_pages=ref_pages,
            )
    except TokenBudgetError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    display_analysis(result)

    if not no_save:
        out_dir = Path(output_dir) if output_dir else settings.get_output_path()
        saved_path = save_analysis(result, out_dir)
        console.print(f"\n[green]Analysis saved to: {saved_path}[/green]")


@library_app.command("add")
def library_add(
    pdfs: Annotated[list[Path], typer.Argument(help="PDF files to add")],
) -> None:
    """Add technique PDFs to the reference library."""
    try:
        added = add_pdfs(pdfs)
        for name in added:
            console.print(f"[green]Added: {name}[/green]")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@library_app.command("remove")
def library_remove(
    name: Annotated[str, typer.Argument(help="Name of the PDF to remove")],
) -> None:
    """Remove a PDF from the reference library."""
    if remove_pdf(name):
        console.print(f"[green]Removed: {name}[/green]")
    else:
        console.print(f"[red]Not found: {name}[/red]")
        raise typer.Exit(1)


@library_app.command("list")
def library_list() -> None:
    """List all PDFs in the reference library."""
    entries = list_pdfs()
    if not entries:
        console.print(
            "[yellow]Library is empty. "
            "Add PDFs with: notes library add <PDF>[/yellow]"
        )
        return

    table = Table(title="Reference Library")
    table.add_column("Name", style="cyan")
    table.add_column("Pages", justify="right")
    table.add_column("Size", justify="right")

    for entry in entries:
        size_mb = entry.size_bytes / (1024 * 1024)
        table.add_row(entry.name, str(entry.pages), f"{size_mb:.1f} MB")

    console.print(table)


@config_app.command("show")
def config_show() -> None:
    """Show current configuration."""
    settings = get_settings()
    table = Table(title="Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    table.add_row("model", settings.model)
    table.add_row("output_dir", settings.output_dir)
    table.add_row("library_dir", settings.library_dir)
    table.add_row("max_tokens", f"{settings.max_tokens:,}")
    if settings.anthropic_api_key:
        api_display = "***" + settings.anthropic_api_key[-4:]
    else:
        api_display = "[red]not set[/red]"
    table.add_row("anthropic_api_key", api_display)

    console.print(table)


@config_app.command("set")
def config_set(
    key: Annotated[str, typer.Argument(help="Configuration key")],
    value: Annotated[str, typer.Argument(help="Configuration value")],
) -> None:
    """Update a configuration value."""
    valid_keys = {"model", "output_dir", "library_dir", "max_tokens"}
    if key not in valid_keys:
        valid = ", ".join(sorted(valid_keys))
        console.print(f"[red]Invalid key: {key}. Valid: {valid}[/red]")
        raise typer.Exit(1)

    save_config(key, value)
    console.print(f"[green]Set {key} = {value}[/green]")
