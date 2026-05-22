# 📂 Smart Organizer

Smart file and folder organizer with:
- **GUI Mode (`gui`)**: Modern graphical user interface with dark obsidian theme.
- **Passive Mode (`run`)**: Scan once.
- **Active Mode (`watch`)**: Monitored real-time folder processing with clean start/stop control.
- **Rules defined in TOML**: Highly flexible declarative configuration.
- **Safe simulation with `--dry-run`**: Preview what will happen without touching anything.
- **Rollback support with `--undo`**: Safely undo the last file organization execution.

## Key Behavior: `destination` is relative to `default_destination`
By default, the app creates an output folder inside the watched folder:
- If you watch `~/Downloads` and `default_destination = "Organized"`, then the base folder becomes `~/Downloads/Organized`.

In TOML, each rule's `destination` is interpreted as **relative to** that base folder.
Example:
- `default_destination = "Organized"`
- `destination = "Images"`
→ files/folders go to `~/Downloads/Organized/Images`.

For backward compatibility, if you previously set `destination = "Organized/Images"`, the tool will automatically avoid creating nested paths like `Organized/Organized/Images`.

---

## Installation (Linux/macOS)

```bash
git clone https://github.com/benjamin23k/smart-organizer.git
cd smart-organizer
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Installation (Windows)

```powershell
git clone https://github.com/benjamin23k/smart-organizer.git
cd smart-organizer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

---

## Usage

### 🖥️ Graphical User Interface (GUI)
Start the modernized premium dark-mode interface:
```bash
smart-org gui
```
Or run directly:
```bash
python -m smart_organizer.gui
```

### ⌨️ Command Line Interface (CLI)

Scan once (one-time run):
```bash
smart-org run -c config.toml
```

Watch folders (real-time):
```bash
smart-org watch -c config.toml
```

Dry run (show what would happen, without moving/copying):
```bash
smart-org run -c config.toml --dry-run
```

Undo last execution:
```bash
smart-org run --undo
```

---

## Configuration (TOML)

You should set:
- `general.watch_paths`: Folders to watch (by default, if empty, defaults to current directory).
- `rules`: List of rules defining how to organize.

### File Rule Example:
```toml
[[rules]]
name = "Images"
match_extension = ["jpg", "png", "jpeg", "webp", "avif"]
destination = "Images"
action = "move"
```

### Folder/Directory Rule Example:
You can also match and organize entire directories (folders) by setting `match_folders = true`.
```toml
[[rules]]
name = "Folders"
match_folders = true
destination = "Folders"
action = "move"
```

### Default destination behavior
If a rule does NOT define `destination`, the tool uses `general.default_destination` (defaults to `"Organized"`).

---

## Notes about Windows paths
In Windows, you can use:
- Forward slashes in TOML, e.g. `C:/Users/<user>/Downloads`
- Or `~` if it works for your environment.
