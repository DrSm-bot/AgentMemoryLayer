#!/usr/bin/env python3
"""Manage permanent notes for the agent."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
import uuid

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent
NOTE_FILE = DEFAULT_MEMORY_DIR / "notes.json"

logger = logging.getLogger(__name__)


def load_notes(note_file: Path = NOTE_FILE) -> list[dict]:
    if note_file.exists():
        try:
            with note_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON from %s; returning empty list.", note_file)
    return []


def save_notes(notes: list[dict], note_file: Path = NOTE_FILE) -> None:
    note_file.parent.mkdir(parents=True, exist_ok=True)
    with note_file.open("w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2)


def add_note(content: str, note_file: Path = NOTE_FILE) -> dict:
    notes = load_notes(note_file)
    note = {
        "id": str(uuid.uuid4()),
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
    }
    notes.append(note)
    notes = notes[-10:]
    save_notes(notes, note_file)
    return note


def remove_note(note_id: str, note_file: Path = NOTE_FILE) -> bool:
    notes = load_notes(note_file)
    new_notes = [n for n in notes if n["id"] != note_id]
    if len(new_notes) == len(notes):
        return False
    save_notes(new_notes, note_file)
    return True


def list_notes(note_file: Path = NOTE_FILE) -> list[dict]:
    return load_notes(note_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage permanent notes")
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_MEMORY_DIR,
        help="Directory to store notes.json",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add")
    add_p.add_argument("content")

    sub.add_parser("list")

    remove_p = sub.add_parser("remove")
    remove_p.add_argument("id")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    note_file = args.memory_dir / "notes.json"
    if args.command == "add":
        note = add_note(args.content, note_file=note_file)
        print(note["id"])
    elif args.command == "list":
        notes = list_notes(note_file=note_file)
        print(json.dumps(notes, indent=2))
    elif args.command == "remove":
        if not remove_note(args.id, note_file=note_file):
            print("Note not found")


if __name__ == "__main__":
    main()
