
Smart file organizer (English) with:
- Passive mode (`run`) to scan once
- Active mode (`watch`) to process new files in real time
- Rules defined in TOML
- Safe simulation with `--dry-run`
- Rollback support with `--undo`

## Key behavior: `destination` is relative to `default_destination`
By default the app creates an output folder inside the watched folder:
- if you watch `~/Downloads` and `default_destination = "Organized"`, then the base becomes `~/Downloads/Organized`.

In TOML, each rule’s `destination` is interpreted as **relative to** that base.
Example:
- `default_destination = "Organized"`
- `destination = "Images"`
→ files go to `~/Downloads/Organized/Images`.

For backward compatibility, if you previously set `destination = "Organized/Images"`, the tool will automatically avoid creating `Organized/Organized/Images`.

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

## Usage

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

## Configuration (TOML)

You should set at least:
- `general.watch_paths`: folders to watch (by default the program tries `~/Downloads` and `~/Desktop`)
- `rules`: rules with `match_extension`, `destination`, and `action`

Example:
```toml
[general]
watch_paths = ["~/Downloads"]

action = "move"  # (optional; action is per rule below)

[[rules]]
name = "Images"
match_extension = ["jpg", "png", "jpeg"]
destination = "Organized/Images"
action = "move"
```

### Default destination behavior
If a rule does NOT define `destination`, the tool uses `general.default_destination`.

- Default value: `general.default_destination = "Organized"`

## Notes about Windows paths
In Windows, you can use:
- forward slashes in TOML, e.g. `C:/Users/<user>/Downloads`
- or `~` if it works for your environment

