import sys
from pathlib import Path
from typing import List, Literal
from pydantic import BaseModel, Field

class General(BaseModel):
    watch_paths: List[Path] = [Path("~/Downloads"), Path("~/Desktop")]
    log_level: str = "INFO"
  
    default_destination: str = "Organized"


class Rule(BaseModel):
    name: str
    match_extension: List[str] = []
    match_size_min: int = 0
    destination: str | None = None
    action: Literal["move", "copy", "symlink"] = "move"
    match_folders: bool = False

class Config(BaseModel):
    general: General = Field(default_factory=General)
    rules: List[Rule] = []

def resolve_config_path(specified_path: Path | None = None) -> Path:
    if specified_path is not None:
        path = specified_path.expanduser().resolve()
        if path.exists():
            return path
    
        raise FileNotFoundError(f"❌ Config not found: {path}")

    
   
    local_path = Path("config.toml").resolve()
    if local_path.exists():
        return local_path

    
    user_config_dir = Path("~/.config/smart-organizer").expanduser()
    user_config_path = user_config_dir / "config.toml"
    if user_config_path.exists():
        return user_config_path

   
    user_home_path = Path("~/.smart-organizer.toml").expanduser()
    if user_home_path.exists():
        return user_home_path

  
    try:
        user_config_dir.mkdir(parents=True, exist_ok=True)
        default_config_content = """[general]
# Folders to watch. If empty, defaults to the current working directory in CLI/GUI.
watch_paths = []
default_destination = "Organized"

[[rules]]
name = "Documents"
match_extension = ["pdf", "docx", "doc", "txt", "xlsx", "xls", "pptx", "ppt", "csv", "odt", "rtf"]
destination = "Documents"
action = "move"

[[rules]]
name = "Images"
match_extension = ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg", "tiff", "heic", "avif"]
destination = "Images"
action = "move"

[[rules]]
name = "Audio"
match_extension = ["mp3", "wav", "flac", "m4a", "ogg", "wma", "aac"]
destination = "Audio"
action = "move"

[[rules]]
name = "Video"
match_extension = ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm"]
destination = "Video"
action = "move"

[[rules]]
name = "Archives"
match_extension = ["zip", "tar", "gz", "rar", "7z", "tgz", "bz2", "xz", "zst", "lz", "cab", "iso", "dmg"]
destination = "Archives"
action = "move"

[[rules]]
name = "Folders"
match_folders = true
destination = "Folders"
action = "move"
"""
        user_config_path.write_text(default_config_content, encoding="utf-8")
        return user_config_path
    except Exception:
       
        try:
            local_path.write_text(default_config_content, encoding="utf-8")
            return local_path
        except Exception:
            return local_path

def load_config(path: Path | None = None) -> Config:
    
    resolved_path = resolve_config_path(path)

    if sys.version_info >= (3, 11):
        import tomllib
        with open(resolved_path, "rb") as f:
            data = tomllib.load(f)
    else:
        import tomli
        with open(resolved_path, "rb") as f:
            data = tomli.load(f)
    cfg = Config(**data)

    if not cfg.general.watch_paths:
        cfg.general.watch_paths = [Path(".").resolve()]

    return cfg

