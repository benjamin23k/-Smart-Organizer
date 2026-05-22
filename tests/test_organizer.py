import pytest
import shutil
import json
from pathlib import Path
from smart_organizer.config import load_config, resolve_config_path, Config, General
from smart_organizer.rules import resolve_destination, Rule, matches
from smart_organizer.utils import execute_action, rollback_history, log_history, HISTORY_FILE
from smart_organizer.organizer import process_path


def test_resolve_config_path_default():
    # If config.toml exists locally, it should return that. If not, it falls back to standard user paths.
    # We can test if resolve_config_path returns a path.
    path = resolve_config_path(None)
    assert isinstance(path, Path)
    assert path.name == "config.toml"


def test_load_config_defaults():
    # Load config without a path should trigger the fallback and create/resolve the config file.
    cfg = load_config(None)
    assert cfg.general.default_destination == "Organized"
    assert len(cfg.rules) > 0
    # Should default watch_paths to CWD since it is empty in the fallback config
    assert len(cfg.general.watch_paths) == 1
    assert cfg.general.watch_paths[0] == Path(".").resolve()


def test_resolve_destination_appends_filename():
    rule = Rule(
        name="Images",
        match_extension=["png"],
        destination="Images",
        action="move"
    )
    base_dir = Path("/tmp/Organized")
    file_path = Path("/tmp/photo.png")
    
    dest_path = resolve_destination(
        file=file_path,
        rule=rule,
        base_dir=base_dir,
        default_destination="Organized"
    )
    
    # Destination should be absolute and end with the filename!
    assert dest_path.name == "photo.png"
    assert dest_path.parent.name == "Images"


def test_matches_folders(tmp_path):
    # Rule configured to match folders
    folder_rule = Rule(
        name="FoldersRule",
        match_folders=True,
        destination="FoldersDest",
        action="move"
    )

    # Rule configured to match files (default)
    file_rule = Rule(
        name="FilesRule",
        match_folders=False,
        destination="FilesDest",
        action="move"
    )

    test_dir = tmp_path / "some_dir"
    test_dir.mkdir()

    test_file = tmp_path / "some_file.txt"
    test_file.write_text("hello")

    # Folder should only match folder_rule, not file_rule
    assert matches(test_dir, folder_rule) is True
    assert matches(test_dir, file_rule) is False

    # File should only match file_rule, not folder_rule
    assert matches(test_file, file_rule) is True
    assert matches(test_file, folder_rule) is False


def test_organize_folder(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create folder to organize inside src
    sub_dir = src_dir / "target_folder"
    sub_dir.mkdir()
    (sub_dir / "data.txt").write_text("some content")

    # Set up config with folders rule
    cfg = Config(
        general=General(
            watch_paths=[src_dir],
            default_destination="Organized"
        ),
        rules=[
            Rule(
                name="Folders",
                match_folders=True,
                destination="Folders",
                action="move"
            )
        ]
    )

    process_path(cfg)

    # The sub_dir should have been moved to src/Organized/Folders/target_folder
    expected_path = src_dir / "Organized" / "Folders" / "target_folder"
    assert expected_path.exists()
    assert expected_path.is_dir()
    assert (expected_path / "data.txt").exists()
    assert not sub_dir.exists()


def test_execute_action_copy_folder(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "nested.txt").write_text("nested text")

    dest_dir = tmp_path / "dest" / "src"

    # execute copy action on directory
    success = execute_action(src_dir, dest_dir, "copy", dry_run=False)
    assert success is True
    assert dest_dir.exists()
    assert (dest_dir / "nested.txt").exists()
    assert src_dir.exists()


def test_rollback_folder(tmp_path):
    # Ensure HISTORY_FILE path in test environment points to a temp location
    import smart_organizer.utils
    old_history_file = smart_organizer.utils.HISTORY_FILE
    smart_organizer.utils.HISTORY_FILE = tmp_path / ".smart_org_history.json"

    try:
        src_dir = tmp_path / "original_folder"
        src_dir.mkdir()
        (src_dir / "test.txt").write_text("hello test")

        target_dir = tmp_path / "destination_folder"

        # Simula move
        execute_action(src_dir, target_dir, "move", dry_run=False)
        log_history({"src": str(src_dir), "dest": str(target_dir), "action": "move"})

        assert target_dir.exists()
        assert not src_dir.exists()

        # Rollback
        rollback_history()

        assert src_dir.exists()
        assert (src_dir / "test.txt").exists()
        assert not target_dir.exists()

    finally:
        # Restore original HISTORY_FILE path
        smart_organizer.utils.HISTORY_FILE = old_history_file
