from pathlib import Path
from datetime import datetime
from .config import Rule

def matches(file: Path, rule: Rule) -> bool:
   
    if rule.match_extension:
        ext = file.suffix.lstrip(".").lower()
        if ext not in [e.lower() for e in rule.match_extension]:
            return False
    if rule.match_size_min and file.stat().st_size < rule.match_size_min:
        return False
    return True

def resolve_destination(file: Path, rule: Rule, base_dir: Path, default_destination: str) -> Path:

    now = datetime.now()
    dest = rule.destination or default_destination

    dest = dest.replace("{YYYY}", str(now.year))
    dest = dest.replace("{MM}", str(now.month).zfill(2))
    dest = dest.replace("{DD}", str(now.day).zfill(2))
    dest = dest.replace("{HH}", str(now.hour).zfill(2))
    dest = dest.replace("{EXT}", file.suffix.lstrip("."))
    return (base_dir / dest).resolve()
