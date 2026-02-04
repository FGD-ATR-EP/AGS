"""Genesis Journal CLI application.

Provides a lightweight command-line journal for recording intent-driven notes
within the Aetherium Genesis ecosystem.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "genesis_journal.json"


@dataclass(frozen=True)
class JournalEntry:
    entry_id: str
    timestamp: str
    title: str
    content: str


def _load_entries(path: Path) -> List[JournalEntry]:
    if not path.exists():
        return []
    raw_entries = json.loads(path.read_text(encoding="utf-8"))
    return [JournalEntry(**entry) for entry in raw_entries]


def _save_entries(path: Path, entries: List[JournalEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(entry) for entry in entries]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _generate_entry_id(entries: List[JournalEntry]) -> str:
    existing_ids = {entry.entry_id for entry in entries}
    next_index = len(entries) + 1
    while True:
        candidate = f"GJ-{next_index:04d}"
        if candidate not in existing_ids:
            return candidate
        next_index += 1


def add_entry(title: str, content: str, path: Path = DATA_FILE) -> JournalEntry:
    entries = _load_entries(path)
    entry = JournalEntry(
        entry_id=_generate_entry_id(entries),
        timestamp=datetime.now(timezone.utc).isoformat(),
        title=title.strip(),
        content=content.strip(),
    )
    entries.append(entry)
    _save_entries(path, entries)
    return entry


def list_entries(limit: int, path: Path = DATA_FILE) -> List[JournalEntry]:
    entries = _load_entries(path)
    return list(reversed(entries[-limit:])) if limit > 0 else list(reversed(entries))


def clear_entries(path: Path = DATA_FILE) -> None:
    _save_entries(path, [])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Genesis Journal: capture intent-driven notes.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new journal entry")
    add_parser.add_argument("--title", required=True, help="Short title for the entry")
    add_parser.add_argument("--content", required=True, help="Full content of the entry")

    list_parser = subparsers.add_parser("list", help="List recent journal entries")
    list_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of entries to show (0 for all)",
    )

    clear_parser = subparsers.add_parser("clear", help="Clear all journal entries")
    clear_parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm clearing without additional prompts",
    )

    return parser


def _format_entry(entry: JournalEntry) -> str:
    return (
        f"[{entry.entry_id}] {entry.title}\n"
        f"  {entry.timestamp}\n"
        f"  {entry.content}"
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "add":
        entry = add_entry(args.title, args.content)
        print("Entry saved:\n")
        print(_format_entry(entry))
        return

    if args.command == "list":
        entries = list_entries(args.limit)
        if not entries:
            print("No journal entries found.")
            return
        print("Genesis Journal Entries:\n")
        for entry in entries:
            print(_format_entry(entry))
            print()
        return

    if args.command == "clear":
        if not args.yes:
            print("Refusing to clear entries without --yes confirmation.")
            return
        clear_entries()
        print("Journal cleared.")
        return


if __name__ == "__main__":
    main()
