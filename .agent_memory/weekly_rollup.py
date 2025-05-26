#!/usr/bin/env python3
"""Generate weekly summaries of agent memory and optionally prune old entries."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from summarize_memory_entries import (
    load_entries,
    filter_entries,
    summarize,
)
from prune_memory_entries import determine_files_to_delete

DEFAULT_ENTRIES_DIR = Path(__file__).resolve().parent / "entries"
DEFAULT_SUMMARY_DIR = Path(__file__).resolve().parent / "weekly_summaries"
DEFAULT_SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


def last_week_range() -> tuple[str, str]:
    """Return ISO timestamps for the start and end of last week (UTC)."""
    now = datetime.utcnow()
    start_this_week = now - timedelta(days=now.weekday())
    start_this_week = start_this_week.replace(hour=0, minute=0, second=0, microsecond=0)
    start_last_week = start_this_week - timedelta(days=7)
    end_last_week = start_this_week - timedelta(microseconds=1)
    return start_last_week.isoformat(), end_last_week.isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create last week's memory summary and optionally prune old entries"
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_ENTRIES_DIR,
        help="Path to memory entries directory",
    )
    parser.add_argument(
        "--summary-dir",
        type=Path,
        default=DEFAULT_SUMMARY_DIR,
        help="Directory to write weekly summaries",
    )
    prune = parser.add_argument_group("pruning")
    prune.add_argument(
        "--older-than", type=int, help="Delete entries older than N days"
    )
    prune.add_argument(
        "--keep-last", type=int, help="Keep only the most recent N entries"
    )
    prune.add_argument(
        "--dry-run", action="store_true", help="List files that would be deleted"
    )
    return parser.parse_args()


def run_summary(memory_dir: Path, summary_dir: Path) -> Path:
    since, until = last_week_range()
    entries = load_entries(memory_dir)
    entries = filter_entries(entries, since, until)
    summary = summarize(entries, since, until)
    output = (
        summary_dir / f"summary_{since.split('T')[0]}_to_{until.split('T')[0]}.json"
    )
    with output.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote summary to {output}")
    return output


def run_prune(
    memory_dir: Path, older_than: int | None, keep_last: int | None, dry_run: bool
) -> None:
    if older_than is None and keep_last is None:
        return
    args = SimpleNamespace(
        before=None, older_than=older_than, keep_last=keep_last, memory_dir=memory_dir
    )
    files = determine_files_to_delete(args)
    if not files:
        print("No entries to delete")
        return
    for f in files:
        if dry_run:
            print(f"Would delete {f}")
        else:
            f.unlink(missing_ok=True)
            print(f"Deleted {f}")


def main() -> None:
    args = parse_args()
    run_summary(args.memory_dir, args.summary_dir)
    run_prune(args.memory_dir, args.older_than, args.keep_last, args.dry_run)


if __name__ == "__main__":
    main()
