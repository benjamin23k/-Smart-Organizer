import typer
from rich.console import Console
from pathlib import Path

from .config import load_config
from .organizer import process_path
from .utils import rollback_history as rollback
from .watcher import start

console = Console()
app = typer.Typer(help="📂 Smart Organizer: Organize files automatically", add_completion=False)


@app.command()
def run(
    path: str = typer.Argument(None, help="Folder to organize (defaults to current directory if not configured)"),
    config: str = typer.Option("config.toml", "--config", "-c", help="Path to TOML config"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without moving"),
    undo: bool = typer.Option(False, "--undo", help="Undo the last execution"),
    output_dir: str | None = typer.Option(
        None, "--output-dir", help="Override the destination base (e.g. ./Organized)"
    ),
    watch_dir: str | None = typer.Option(
        None, "--watch-dir", help="Override the folder to scan/watch (e.g. ~/Downloads)"
    ),
):
    """Run once."""
    cfg_path = Path(config)
    if config == "config.toml" and not cfg_path.exists():
        cfg = load_config(None)
    else:
        cfg = load_config(cfg_path)

    if undo:
        rollback()
        return

    target_dir = path or watch_dir
    if target_dir:
        cfg.general.watch_paths = [Path(target_dir).expanduser().resolve()]

    if output_dir:
       
        cfg.general.default_destination = str(Path(output_dir).expanduser().resolve())

    console.print(f"🚀 Scanning: {cfg.general.watch_paths}")
    process_path(cfg, dry_run=dry_run)


@app.command()
def watch(
    path: str = typer.Argument(None, help="Folder to watch (defaults to current directory if not configured)"),
    config: str = typer.Option("config.toml", "--config", "-c"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    output_dir: str | None = typer.Option(
        None, "--output-dir", help="Override the destination base (e.g. ./Organized)"
    ),
    watch_dir: str | None = typer.Option(
        None, "--watch-dir", help="Override the folder to scan/watch (e.g. ~/Downloads)"
    ),
):
    """Watch for new files and organize them in real time."""
    cfg_path = Path(config)
    if config == "config.toml" and not cfg_path.exists():
        cfg = load_config(None)
    else:
        cfg = load_config(cfg_path)

    target_dir = path or watch_dir
    if target_dir:
        cfg.general.watch_paths = [Path(target_dir).expanduser().resolve()]

    if output_dir:
        cfg.general.default_destination = str(Path(output_dir).expanduser().resolve())

    start(cfg, dry_run=dry_run)


@app.command()
def gui():
    """Launch the graphical user interface."""
    try:
        from .gui import run_gui
        run_gui()
    except (ImportError, ModuleNotFoundError, AttributeError):
        console.print("[bold red]Error: Tkinter is not installed or GUI is not supported on this system.[/bold red]")
        console.print("[yellow]Please install python3-tk or run the CLI commands instead.[/yellow]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

