# mypy: ignore-errors
#!/usr/bin/env python3
"""Summarize agent memory entries over a time range."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from jsonschema import ValidationError, validate

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent / "entries"
DEFAULT_SUMMARY_DIR = Path(__file__).resolve().parent / "weekly_summaries"
DEFAULT_SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize agent memory entries")
    parser.add_argument("--since", help="Start ISO timestamp", required=True)
    parser.add_argument("--until", help="End ISO timestamp", required=True)
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_MEMORY_DIR,
        help="Path to memory entries directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output summary file (defaults to weekly_summaries)",
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
    return entries


def filter_entries(entries: Iterable[dict], since: str, until: str) -> List[dict]:
    since_dt = datetime.fromisoformat(since)
    until_dt = datetime.fromisoformat(until)
    result: List[dict] = []
    for e in entries:
        ts = datetime.fromisoformat(e["ts"])
        if since_dt <= ts <= until_dt:
            result.append(e)
    return result


def summarize(entries: Iterable[dict], since: str, until: str) -> dict:
    tag_counter: Counter[str] = Counter()
    contexts: List[str] = []
    reflections: List[str] = []
    for e in entries:
        tag_counter.update(e.get("tags", []))
        contexts.append(e["context"])
        reflections.append(e["reflection"])
    return {
        "start": since,
        "end": until,
        "entry_count": len(contexts),
        "tag_counts": dict(tag_counter),
        "contexts": contexts,
        "reflections": reflections,
    }


def main() -> None:
    args = parse_args()
    entries = load_entries(args.memory_dir)
    entries = filter_entries(entries, args.since, args.until)
    summary = summarize(entries, args.since, args.until)
    output_path = args.output
    if output_path is None:
        start = args.since.split("T")[0]
        end = args.until.split("T")[0]
        output_path = DEFAULT_SUMMARY_DIR / f"summary_{start}_to_{end}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote summary to {output_path}")


if __name__ == "__main__":
    main()
