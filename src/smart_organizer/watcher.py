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
        p = Path(event.src_path)

      
        if p.name.startswith("."):
            return

        
        for watch_path in self.cfg.general.watch_paths:
            output_base = Path(watch_path).expanduser().resolve() / self.cfg.general.default_destination
            try:
                if p.resolve() == output_base.resolve() or output_base.resolve() in p.resolve().parents:
                    return
            except Exception:
                pass

        if time.time() - self._cooldown.get(str(p), 0) < 2:
            return

        self._cooldown[str(p)] = time.time()
        logger.info(f"📥 New item detected: {p.name}")
        process_path(self.cfg, dry_run=self.dry_run)


def start(cfg: Config, dry_run: bool = False, stop_event=None):
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
        while stop_event is None or not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()

