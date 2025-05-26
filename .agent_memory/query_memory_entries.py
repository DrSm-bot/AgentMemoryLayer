# mypy: ignore-errors
#!/usr/bin/env python3
"""Query agent memory entries with simple filters."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from jsonschema import ValidationError, validate

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent / "entries"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query agent memory entries")
    parser.add_argument("--tags", nargs="*", help="Filter by one or more tags")
    parser.add_argument(
        "--since", help="Only include entries on or after this ISO timestamp"
    )
    parser.add_argument("--until", help="Only include entries up to this ISO timestamp")
    parser.add_argument("--last", type=int, help="Show only the N most recent entries")
    parser.add_argument(
        "--search",
        help="Only include entries containing this term in context, observation, or reflection",
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_MEMORY_DIR,
        help="Path to memory entries directory",
    )
    return parser.parse_args()


def load_entries(memory_dir: Path) -> List[dict]:
    entries: List[dict] = []
    with SCHEMA_PATH.open("r", encoding="utf-8") as sf:
        schema = json.load(sf)
    for file in sorted(memory_dir.glob("*.jsonl")):
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    validate(instance=record, schema=schema)
                    entries.append(record)
                except (json.JSONDecodeError, ValidationError) as e:
                    print(f"Skipping invalid entry in {file}: {e}", file=sys.stderr)
    entries.sort(key=lambda e: e["ts"], reverse=True)
    return entries


def filter_entries(
    entries: Iterable[dict],
    tags: list[str] | None,
    since: str | None,
    until: str | None,
    search: str | None,
) -> List[dict]:
    result: List[dict] = []
    since_dt = datetime.fromisoformat(since) if since else None
    until_dt = datetime.fromisoformat(until) if until else None
    for e in entries:
        ts = datetime.fromisoformat(e["ts"])
        if since_dt and ts < since_dt:
            continue
        if until_dt and ts > until_dt:
            continue
        if tags and not set(tags).intersection(e.get("tags", [])):
            continue
        if search:
            haystack = " ".join(
                [
                    e.get("context", ""),
                    e.get("observation", ""),
                    e.get("reflection", ""),
                ]
            ).lower()
            if search.lower() not in haystack:
                continue
        result.append(e)
    return result


def main() -> None:
    args = parse_args()
    entries = load_entries(args.memory_dir)
    entries = filter_entries(entries, args.tags, args.since, args.until, args.search)
    if args.last is not None:
        entries = entries[: args.last]
    for entry in entries:
        print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()
