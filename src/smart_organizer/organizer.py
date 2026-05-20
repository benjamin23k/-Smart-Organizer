from pathlib import Path
from .config import Config
from .rules import matches, resolve_destination
from .utils import setup_logger, log_history, execute_action

logger = setup_logger("INFO")

def process_path(cfg: Config, dry_run: bool = False):
    for p in cfg.general.watch_paths:
        src = Path(p).expanduser()
        if not src.exists():
            logger.warning(f"⚠️ Ruta ignorada: {src}")
            continue
            
        for file in src.iterdir():
            if file.is_dir(): continue
            
            for rule in cfg.rules:
                if matches(file, rule):
                    target = resolve_destination(file, rule, src, cfg.general.default_destination)
                    if execute_action(file, target, rule.action, dry_run):
                        log_history({"src": str(file), "dest": str(target), "action": rule.action})
                        logger.info(f"✅ {file.name} → {rule.name}")
                    break