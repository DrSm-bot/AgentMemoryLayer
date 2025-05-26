#!/usr/bin/env python3
"""Utility to append a new agent memory entry."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
import uuid

from jsonschema import validate

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent


def load_schema(schema_path: Path) -> dict:
    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Append an agent memory entry")
    parser.add_argument("context", help="Short description of files or task")
    parser.add_argument("observation", help="Summary of the outcome")
    parser.add_argument("reflection", help="What to improve next time")
    parser.add_argument("--tags", nargs="*", default=[], help="Optional tags")
    parser.add_argument("--task-id", help="ID of related task")
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_MEMORY_DIR,
        help="Root directory for agent memory",
    )
    args = parser.parse_args()

    memory_dir = args.memory_dir
    entries_dir = memory_dir / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)
    schema_path = memory_dir / "schema.json"

    entry = {
        "ts": datetime.utcnow().isoformat(),
        "agent": os.getenv("CODEX_AGENT", "codex"),
        "run_id": str(uuid.uuid4()),
        "context": args.context,
        "observation": args.observation,
        "reflection": args.reflection,
        "tags": args.tags,
    }
    if args.task_id:
        entry["task_id"] = args.task_id

    schema = load_schema(schema_path)
    validate(instance=entry, schema=schema)

    filename = entries_dir / f"{entry['ts']}.jsonl"
    with filename.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    main()
