# Agent Memory Layer

This directory stores lightweight logs of previous Codex runs. Each iteration appends a JSON line file in `entries/` capturing context, observations, and a short reflection. Older logs may be summarized into `weekly_summaries/`.

Agents should review the most recent relevant entries before modifying files and write a new entry when done.

## Adding an Entry

Use `.agent_memory/memory_cli.py add` to append a new memory record after each run:

```bash
.agent_memory/memory_cli.py add "<context>" "<observation>" "<reflection>" --tags tag1 tag2 --memory-dir .agent_memory
```

All memory entries must conform to `schema.json`. `.agent_memory/memory_cli.py add`
loads this schema and validates each record before writing it. The query and
summary scripts also validate loaded files and ignore any that fail validation.

## Querying Entries

Use `.agent_memory/memory_cli.py query` to list past runs. You can filter by tags, time range, or search text and limit the results:

```bash
.agent_memory/memory_cli.py query --tags bugfix --since 2025-05-01T00:00:00 --last 5
.agent_memory/memory_cli.py query --search "error" --last 3
```
The `--search` flag matches entries where the term appears in the `context`, `observation`, or `reflection` fields.

## Summarizing History

To generate a simple JSON summary of a period, run:

```bash
.agent_memory/memory_cli.py summarize --since 2025-05-01T00:00:00 --until 2025-05-07T00:00:00
```

The summary is written under `weekly_summaries/` by default.

## Exporting to Markdown

To share recent memory entries in a more readable format you can export them to
a Markdown file:

```bash
.agent_memory/export_memory_markdown.py --output memory.md --last 5
```

Filters such as `--tags`, `--since`, and `--until` work the same as in the query
script.

## Pruning Old Entries

Use `.agent_memory/memory_cli.py prune` to remove old memory files and keep the directory manageable. You can delete entries before a specific timestamp, older than a number of days, or keep only the most recent N entries.

```bash
# Delete entries older than 30 days
.agent_memory/memory_cli.py prune --older-than 30

# Keep only the last 100 entries
.agent_memory/memory_cli.py prune --keep-last 100
```

## Weekly Rollups

`.agent_memory/weekly_rollup.py` automates summarizing the previous week's entries and
optionally pruning older logs. It writes the summary to `weekly_summaries/` and
accepts the same pruning options as `prune_memory_entries.py`.

```bash
# Summarize last week and remove entries older than 30 days
.agent_memory/weekly_rollup.py --older-than 30
```

This script can be scheduled via cron or a CI job. For example, run every Monday
at midnight:

```cron
0 0 * * MON /path/to/repo/.agent_memory/weekly_rollup.py --older-than 30
```

## Task List

A lightweight task list helps the agent keep track of ongoing work. Tasks are stored in `tasks.json` and have a status of `open`, `in_progress`, or `finished`. Only the ten most recent tasks are kept.

```bash
# Add a task
.agent_memory/memory_cli.py task add "Implement scoring system" --memory-dir .agent_memory

# Update a task
.agent_memory/memory_cli.py task update <task_id> --status in_progress --memory-dir .agent_memory

# List tasks
.agent_memory/memory_cli.py task list --memory-dir .agent_memory
```

## Permanent Notes

Important notes that should persist across runs can be stored in `notes.json`. Up to ten notes are retained.

```bash
# Add a note
.agent_memory/memory_cli.py note add "Review whitepaper weekly" --memory-dir .agent_memory

# List notes
.agent_memory/memory_cli.py note list --memory-dir .agent_memory
```
