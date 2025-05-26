#!/usr/bin/env python3
"""Export agent memory entries to a Markdown file."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from jsonschema import ValidationError, validate

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent / "entries"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export memory entries to Markdown")
    parser.add_argument(
        "--output", type=Path, required=True, help="Markdown output file"
    )
    parser.add_argument("--tags", nargs="*", help="Filter by tags")
    parser.add_argument("--since", help="Start ISO timestamp")
    parser.add_argument("--until", help="End ISO timestamp")
    parser.add_argument(
        "--last", type=int, help="Only export the N most recent entries"
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_MEMORY_DIR,
        help="Memory entries directory",
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
                except (json.JSONDecodeError, ValidationError):
                    continue
    entries.sort(key=lambda e: e["ts"], reverse=True)
    return entries


def filter_entries(
    entries: Iterable[dict],
    tags: list[str] | None,
    since: str | None,
    until: str | None,
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
        result.append(e)
    return result


def entries_to_markdown(entries: Iterable[dict]) -> str:
    lines = []
    for e in reversed(list(entries)):
        ts = e["ts"]
        context = e.get("context", "")
        lines.append(f"## {ts} - {context}")
        lines.append("")
        lines.append(f"- Observation: {e.get('observation','')}")
        lines.append(f"- Reflection: {e.get('reflection','')}")
        if e.get("tags"):
            lines.append(f"- Tags: {', '.join(e['tags'])}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    entries = load_entries(args.memory_dir)
    entries = filter_entries(entries, args.tags, args.since, args.until)
    if args.last is not None:
        entries = entries[: args.last]
    md = entries_to_markdown(entries)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {len(entries)} entries to {args.output}")


if __name__ == "__main__":
    main()
