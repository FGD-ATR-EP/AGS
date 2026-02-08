from pathlib import Path

from src.backend.apps.genesis_journal import add_entry, clear_entries, list_entries


def test_add_and_list_entries(tmp_path: Path) -> None:
    data_path = tmp_path / "journal.json"

    first = add_entry("Intent A", "Content A", path=data_path)
    second = add_entry("Intent B", "Content B", path=data_path)

    assert first.entry_id == "GJ-0001"
    assert second.entry_id == "GJ-0002"

    listed = list_entries(limit=10, path=data_path)
    assert [entry.entry_id for entry in listed] == ["GJ-0002", "GJ-0001"]
    assert listed[0].title == "Intent B"


def test_clear_entries(tmp_path: Path) -> None:
    data_path = tmp_path / "journal.json"
    add_entry("Intent", "Content", path=data_path)

    clear_entries(path=data_path)

    assert list_entries(limit=10, path=data_path) == []
