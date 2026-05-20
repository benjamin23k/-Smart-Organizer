import json
import logging
import shutil
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console()
HISTORY_FILE = Path(".smart_org_history.json")


def setup_logger(level: str = "INFO") -> logging.Logger:
    """Configure logging with colors and clean tracebacks."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )
    return logging.getLogger("smart_organizer")


def log_history(entry: dict) -> None:
    """Save a history entry to enable --undo."""
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text())
        except json.JSONDecodeError:
            history = []
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def execute_action(file: Path, target: Path, action: str, dry_run: bool) -> bool:
    """Execute move/copy/symlink, or simulate in dry-run."""
    if dry_run:
        console.print(f"🔍 [DRY] {action} {file.name} -> {target}")
        return True

    target.parent.mkdir(parents=True, exist_ok=True)

    if action == "move":
        shutil.move(str(file), str(target))
    elif action == "copy":
        shutil.copy2(str(file), str(target))
    elif action == "symlink":
        target.symlink_to(file.resolve())
    else:
        console.print(f"⚠️ Unknown action: {action}")
        return False

    return True


def rollback_history() -> bool:
    """Undo the last recorded execution."""
    if not HISTORY_FILE.exists():
        console.print("ℹ️ Nothing to undo.")
        return False

    try:
        history = json.loads(HISTORY_FILE.read_text())
    except json.JSONDecodeError:
        console.print("⚠️ Corrupted history file. Deleting it.")
        HISTORY_FILE.unlink()
        return False

    for entry in reversed(history):
        src, dest = Path(entry["src"]), Path(entry["dest"])

        if dest.exists():
            if entry["action"] == "move" and not src.exists():
                dest.rename(src)
            elif entry["action"] in ("copy", "symlink"):
                dest.unlink()

    HISTORY_FILE.unlink()
    console.print("↩️ Rollback completed.")
    return True

