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
    cfg = load_config(Path(config))

    if undo:
        rollback()
        return

    if watch_dir:
        cfg.general.watch_paths = [Path(watch_dir).expanduser().resolve()]

    if output_dir:
        # Explicit override: destination base becomes exactly this path.
        cfg.general.default_destination = str(Path(output_dir).expanduser().resolve())

    console.print(f"🚀 Scanning: {cfg.general.watch_paths}")
    process_path(cfg, dry_run=dry_run)


@app.command()
def watch(
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
    cfg = load_config(Path(config))

    if watch_dir:
        cfg.general.watch_paths = [Path(watch_dir).expanduser().resolve()]

    if output_dir:
        cfg.general.default_destination = str(Path(output_dir).expanduser().resolve())

    start(cfg, dry_run=dry_run)


if __name__ == "__main__":
    app()

