import typer
from rich.console import Console
from .config import load_config
from .organizer import process_path
from .utils import rollback_history as rollback

from .watcher import start

console = Console()
app = typer.Typer(help="📂 Smart Organizer: Organiza archivos automáticamente", add_completion=False)

@app.command()
def run(
    config: str = typer.Option("config.toml", "--config", "-c", help="Ruta al TOML"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simula sin mover"),
    undo: bool = typer.Option(False, "--undo", help="Deshace última ejecución"),
):
    """Organiza una sola vez."""
    from pathlib import Path
    cfg = load_config(Path(config))

    if undo:
        rollback()
        return
    console.print(f"🚀 Escaneando: {cfg.general.watch_paths}")
    process_path(cfg, dry_run=dry_run)


@app.command()
def watch(
    config: str = typer.Option("config.toml", "--config", "-c"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
  
    cfg = load_config(config)
    start(cfg, dry_run=dry_run)

if __name__ == "__main__":
    app()