#!/usr/bin/env python3
"""Prune agent memory entries by age or count."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent / "entries"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete old agent memory entries")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--before", help="Delete entries before this ISO timestamp")
    group.add_argument(
        "--older-than", type=int, help="Delete entries older than N days"
    )
    group.add_argument(
        "--keep-last", type=int, help="Keep only the most recent N entries"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="List files that would be deleted"
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_MEMORY_DIR,
        help="Path to memory entries directory",
    )
    return parser.parse_args(argv)


def determine_files_to_delete(args: argparse.Namespace) -> list[Path]:
    files = sorted(args.memory_dir.glob("*.jsonl"))
    if args.keep_last is not None:
        return files[: -args.keep_last]

    if args.before:
        cutoff = datetime.fromisoformat(args.before)
    elif args.older_than is not None:
        cutoff = datetime.utcnow() - timedelta(days=args.older_than)
    else:
        return []

    to_delete = []
    for f in files:
        try:
            ts = datetime.fromisoformat(f.stem)
        except ValueError:
            continue
        if ts < cutoff:
            to_delete.append(f)
    return to_delete


def main() -> None:
    args = parse_args()
    files_to_delete = determine_files_to_delete(args)
    if not files_to_delete:
        print("No entries to delete")
        return
    for f in files_to_delete:
        if args.dry_run:
            print(f"Would delete {f}")
        else:
            f.unlink(missing_ok=True)
            print(f"Deleted {f}")


if __name__ == "__main__":
    main()
