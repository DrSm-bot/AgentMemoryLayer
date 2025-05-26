#!/usr/bin/env python3
"""Unified CLI for agent memory management."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
import uuid

from jsonschema import validate

# Reuse helper functions from existing scripts
import add_memory_entry as add_mod
import query_memory_entries as query_mod
import summarize_memory_entries as summary_mod
import prune_memory_entries as prune_mod
import manage_tasks as task_mod
import manage_notes as note_mod

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent
DEFAULT_ENTRIES_DIR = DEFAULT_MEMORY_DIR / "entries"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage agent memory and notes")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="Append a memory entry")
    add_p.add_argument("context")
    add_p.add_argument("observation")
    add_p.add_argument("reflection")
    add_p.add_argument("--tags", nargs="*", default=[])
    add_p.add_argument("--memory-dir", type=Path, default=DEFAULT_MEMORY_DIR)

    query_p = sub.add_parser("query", help="Query memory entries")
    query_p.add_argument("--tags", nargs="*")
    query_p.add_argument("--since")
    query_p.add_argument("--until")
    query_p.add_argument("--last", type=int)
    query_p.add_argument("--search")
    query_p.add_argument("--memory-dir", type=Path, default=DEFAULT_ENTRIES_DIR)

    sum_p = sub.add_parser("summarize", help="Summarize memory entries")
    sum_p.add_argument("--since", required=True)
    sum_p.add_argument("--until", required=True)
    sum_p.add_argument("--memory-dir", type=Path, default=DEFAULT_ENTRIES_DIR)
    sum_p.add_argument("--output", type=Path)

    prune_p = sub.add_parser("prune", help="Prune memory entries")
    g = prune_p.add_mutually_exclusive_group()
    g.add_argument("--before")
    g.add_argument("--older-than", type=int)
    g.add_argument("--keep-last", type=int)
    prune_p.add_argument("--dry-run", action="store_true")
    prune_p.add_argument("--memory-dir", type=Path, default=DEFAULT_ENTRIES_DIR)

    task_p = sub.add_parser("task", help="Manage task list")
    task_p.add_argument("--memory-dir", type=Path, default=DEFAULT_MEMORY_DIR)
    task_sub = task_p.add_subparsers(dest="task_cmd", required=True)
    t_add = task_sub.add_parser("add")
    t_add.add_argument("description")
    t_upd = task_sub.add_parser("update")
    t_upd.add_argument("id")
    t_upd.add_argument("--status", choices=["open", "in_progress", "finished"])
    t_upd.add_argument("--description")
    task_sub.add_parser("list")
    t_rm = task_sub.add_parser("remove")
    t_rm.add_argument("id")

    note_p = sub.add_parser("note", help="Manage permanent notes")
    note_p.add_argument("--memory-dir", type=Path, default=DEFAULT_MEMORY_DIR)
    note_sub = note_p.add_subparsers(dest="note_cmd", required=True)
    n_add = note_sub.add_parser("add")
    n_add.add_argument("content")
    note_sub.add_parser("list")
    n_rm = note_sub.add_parser("remove")
    n_rm.add_argument("id")

    return parser.parse_args(argv)


def handle_add(args: argparse.Namespace) -> None:
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

    schema = add_mod.load_schema(schema_path)
    validate(instance=entry, schema=schema)
    filename = entries_dir / f"{entry['ts']}.jsonl"
    with filename.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def handle_query(args: argparse.Namespace) -> None:
    entries = query_mod.load_entries(args.memory_dir)
    entries = query_mod.filter_entries(
        entries, args.tags, args.since, args.until, args.search
    )
    if args.last is not None:
        entries = entries[: args.last]
    for e in entries:
        print(json.dumps(e, indent=2))


def handle_summarize(args: argparse.Namespace) -> None:
    entries = summary_mod.load_entries(args.memory_dir)
    entries = summary_mod.filter_entries(entries, args.since, args.until)
    summary = summary_mod.summarize(entries, args.since, args.until)
    output_path = args.output
    if output_path is None:
        start = args.since.split("T")[0]
        end = args.until.split("T")[0]
        output_path = (
            DEFAULT_MEMORY_DIR / "weekly_summaries" / f"summary_{start}_to_{end}.json"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote summary to {output_path}")


def handle_prune(args: argparse.Namespace) -> None:
    files = prune_mod.determine_files_to_delete(args)
    if not files:
        print("No entries to delete")
        return
    for f in files:
        if args.dry_run:
            print(f"Would delete {f}")
        else:
            f.unlink(missing_ok=True)
            print(f"Deleted {f}")


def handle_task(args: argparse.Namespace) -> None:
    task_file = args.memory_dir / "tasks.json"
    if args.task_cmd == "add":
        task = task_mod.add_task(args.description, task_file=task_file)
        print(task["id"])
    elif args.task_cmd == "update":
        if not task_mod.update_task(
            args.id, args.status, args.description, task_file=task_file
        ):
            print("Task not found")
    elif args.task_cmd == "list":
        tasks = task_mod.list_tasks(task_file=task_file)
        print(json.dumps(tasks, indent=2))
    elif args.task_cmd == "remove":
        if not task_mod.remove_task(args.id, task_file=task_file):
            print("Task not found")


def handle_note(args: argparse.Namespace) -> None:
    note_file = args.memory_dir / "notes.json"
    if args.note_cmd == "add":
        note = note_mod.add_note(args.content, note_file=note_file)
        print(note["id"])
    elif args.note_cmd == "list":
        notes = note_mod.list_notes(note_file=note_file)
        print(json.dumps(notes, indent=2))
    elif args.note_cmd == "remove":
        if not note_mod.remove_note(args.id, note_file=note_file):
            print("Note not found")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.command == "add":
        handle_add(args)
    elif args.command == "query":
        handle_query(args)
    elif args.command == "summarize":
        handle_summarize(args)
    elif args.command == "prune":
        handle_prune(args)
    elif args.command == "task":
        handle_task(args)
    elif args.command == "note":
        handle_note(args)


if __name__ == "__main__":
    main()
