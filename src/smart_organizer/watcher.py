import logging
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import Config
from .organizer import process_path

logger = logging.getLogger(__name__)


class _Handler(FileSystemEventHandler):
    def __init__(self, cfg: Config, dry_run: bool):
        self.cfg, self.dry_run = cfg, dry_run
        self._cooldown: dict[str, float] = {}

    def on_created(self, event):
        if event.is_directory:
            return

        p = Path(event.src_path)
        if time.time() - self._cooldown.get(str(p), 0) < 2:
            return

        self._cooldown[str(p)] = time.time()
        logger.info(f"📥 New file detected: {p.name}")
        process_path(self.cfg, dry_run=self.dry_run)


def start(cfg: Config, dry_run: bool = False):
    observer = Observer()

    for p in cfg.general.watch_paths:
        path = Path(str(p)).expanduser()
        if path.exists():
            observer.schedule(_Handler(cfg, dry_run), str(path), recursive=False)
        else:
            logger.warning(f"⚠️ Ignoring path: {path}")

    observer.start()
    logger.info("📀 Watch mode started. Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

