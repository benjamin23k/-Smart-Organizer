import sys
from pathlib import Path
from typing import List, Literal
from pydantic import BaseModel, Field

class General(BaseModel):
    watch_paths: List[Path] = [Path("~/Downloads"), Path("~/Desktop")]
    log_level: str = "INFO"
    # Usado cuando una regla no define destination
    default_destination: str = "Organizado"

class Rule(BaseModel):
    name: str
    match_extension: List[str] = []
    match_size_min: int = 0
    destination: str | None = None
    action: Literal["move", "copy", "symlink"] = "move"

class Config(BaseModel):
    general: General = Field(default_factory=General)
    rules: List[Rule] = []

def load_config(path: Path) -> Config:
    # Acepta rutas con ~ y convierte a ruta absoluta
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"❌ Config no encontrado: {path}")

    if sys.version_info >= (3, 11):
        import tomllib
        with open(path, "rb") as f:
            data = tomllib.load(f)
    else:
        import tomli
        with open(path, "rb") as f:
            data = tomli.load(f)
    return Config(**data)