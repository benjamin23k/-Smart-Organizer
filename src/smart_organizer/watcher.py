import time, logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .config import Config
from .organizer import process_path



logger = logging.getLogger(__name__)

class _Handler(FileSystemEventHandler):
    def __init__(self, cfg: Config, dry_run: bool):
        self.cfg, self.dry_run = cfg, dry_run
        self._cooldown = {}

    def on_created(self, event):
        if event.is_directory: return
        p = Path(event.src_path)
        if time.time() - self._cooldown.get(str(p), 0) < 2: return
        self._cooldown[str(p)] = time.time()
        logger.info(f"📥 Nuevo archivo detectado: {p.name}")
        process_path(self.cfg, dry_run=self.dry_run)


def start(cfg: Config, dry_run: bool = False):
    observer = Observer()
    for p in cfg.general.watch_paths:
        path = Path(p).expanduser()
        if path.exists():
            observer.schedule(_Handler(cfg, dry_run), str(path), recursive=False)
        else:
            logger.warning(f"⚠️ Ruta ignorada: {path}")
    observer.start()
    logger.info("👀 Modo activo iniciado. Ctrl+C para salir.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()