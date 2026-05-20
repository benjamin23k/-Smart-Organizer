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

    # If a rule sets destination, it's interpreted as relative to the default
    # destination base (so you typically write: "Images" not "Organized/Images").
    dest_str = rule.destination or default_destination

    dest_str = dest_str.replace("{YYYY}", str(now.year))
    dest_str = dest_str.replace("{MM}", str(now.month).zfill(2))
    dest_str = dest_str.replace("{DD}", str(now.day).zfill(2))
    dest_str = dest_str.replace("{HH}", str(now.hour).zfill(2))
    dest_str = dest_str.replace("{EXT}", file.suffix.lstrip("."))

    # Backward-compat: if users previously included the default_destination
    # prefix inside `destination` (e.g. "Organized/Images"), strip it to avoid
    # duplicating folders like "Organized/Organized/Images".
    default_prefix = f"{default_destination.rstrip('/')}/"  # normalized
    alt_default_prefix = f"{default_destination.rstrip('/')}$"

    # Do a simple prefix trim with both slash directions.
    if dest_str.startswith(default_prefix):
        dest_str = dest_str[len(default_prefix) :]
    elif dest_str.startswith("/" + default_destination.rstrip("/")):
        dest_str = dest_str[len(default_destination) + 2 :]

    dest = Path(dest_str)
    return (base_dir / dest).resolve()

