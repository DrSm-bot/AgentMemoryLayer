#!/usr/bin/env python3
"""Manage the agent task list."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
import uuid

DEFAULT_MEMORY_DIR = Path(__file__).resolve().parent
TASK_FILE = DEFAULT_MEMORY_DIR / "tasks.json"

logger = logging.getLogger(__name__)


def load_tasks(task_file: Path = TASK_FILE) -> list[dict]:
    if task_file.exists():
        try:
            with task_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON from %s; returning empty list.", task_file)
    return []


def save_tasks(tasks: list[dict], task_file: Path = TASK_FILE) -> None:
    task_file.parent.mkdir(parents=True, exist_ok=True)
    with task_file.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def add_task(description: str, task_file: Path = TASK_FILE) -> dict:
    tasks = load_tasks(task_file)
    task = {
        "id": str(uuid.uuid4()),
        "description": description,
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
    }
    tasks.append(task)
    tasks = tasks[-10:]
    save_tasks(tasks, task_file)
    return task


def update_task(
    task_id: str,
    status: str | None = None,
    description: str | None = None,
    task_file: Path = TASK_FILE,
) -> bool:
    tasks = load_tasks(task_file)
    updated = False
    for t in tasks:
        if t["id"] == task_id:
            if status:
                if status not in {"open", "in_progress", "finished"}:
                    raise ValueError("Invalid status")
                t["status"] = status
            if description is not None:
                t["description"] = description
            updated = True
            break
    if updated:
        save_tasks(tasks, task_file)
    return updated


def remove_task(task_id: str, task_file: Path = TASK_FILE) -> bool:
    tasks = load_tasks(task_file)
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        return False
    save_tasks(new_tasks, task_file)
    return True


def list_tasks(task_file: Path = TASK_FILE) -> list[dict]:
    return load_tasks(task_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage agent tasks")
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=DEFAULT_MEMORY_DIR,
        help="Directory to store tasks.json",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add")
    add_p.add_argument("description")

    update_p = sub.add_parser("update")
    update_p.add_argument("id")
    update_p.add_argument("--status", choices=["open", "in_progress", "finished"])
    update_p.add_argument("--description")

    sub.add_parser("list")

    remove_p = sub.add_parser("remove")
    remove_p.add_argument("id")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    task_file = args.memory_dir / "tasks.json"
    if args.command == "add":
        task = add_task(args.description, task_file=task_file)
        print(task["id"])
    elif args.command == "update":
        if not update_task(args.id, args.status, args.description, task_file=task_file):
            print("Task not found")
    elif args.command == "list":
        tasks = list_tasks(task_file=task_file)
        print(json.dumps(tasks, indent=2))
    elif args.command == "remove":
        if not remove_task(args.id, task_file=task_file):
            print("Task not found")


if __name__ == "__main__":
    main()
