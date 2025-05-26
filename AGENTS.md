# AI Agent Guidelines for [Your Project Name]

Welcome to [Your Project Name]! This guide provides the essential information for AI agents interacting with this project.

## Agent Memory Layer

The `.agent_memory/` directory holds reusable documentation and log history for agents. Read the relevant sections in this document for usage details. Before modifying files, query the five most recent entries with `.agent_memory/memory_cli.py query`. After completing a task, append a new entry that follows `schema.json` using `.agent_memory/memory_cli.py add`. Keep project-specific documentation separate from memory layer docs. Feel free to improve and expand the memory layer but make sure to properly document and test any changes made.

### Agent Guide: Using the Agent Memory Layer

The Agent Memory Layer, located in the `.agent_memory/` directory, is a dedicated module for you, the AI agent, to maintain context, track tasks, and store important notes across your working sessions. This helps you "learn" about the project and its specifics over time.

**The `.agent_memory/memory_cli.py` tool is the preferred way to interact with this layer.**

### Core Workflow

**1. Before Starting Any Task:**

* **Consult Past Memories:** Query recent memory entries to understand previous work and context.
    ```bash
    python .agent_memory/memory_cli.py query --last 5
    ```
    * You can also search by `tags`, `since`, `until`, or `search` terms.
* **Review Current Tasks:** Check your to-do list.
    ```bash
    python .agent_memory/memory_cli.py task list
    ```
    * This will list tasks with their IDs, descriptions, and statuses (`open`, `in_progress`, `finished`).
* **Check Permanent Notes:** Review existing notes for relevant information.
    ```bash
    python .agent_memory/memory_cli.py note list
    ```
    * Notes are for persistent information you might need repeatedly.

**2. After Completing a Task (Before Committing Code):**

* **Add a New Memory Entry:** Log what you did, what the outcome was, and any learnings.
    ```bash
    python .agent_memory/memory_cli.py add "Brief context of the task" "Summary of what was done/observed" "Reflections or what to improve next time" --tags "relevant_tag" "another_tag"
    ```
    * This creates a timestamped JSONL entry in `.agent_memory/entries/`.
    * Entries include `ts` (timestamp), `agent`, `run_id`, `context`, `observation`, `reflection`, and `tags`.
    * Memory entries are validated against `.agent_memory/schema.json`.
* **Update Task Status:** Mark your current task appropriately (e.g., "finished").
    ```bash
    python .agent_memory/memory_cli.py task update <task_id_from_list> --status "finished"
    ```
    * You can also update the description if needed.
* **Add New Notes (If Necessary):** If you learned something persistent that you or another agent might need later, add it as a note.
    ```bash
    python .agent_memory/memory_cli.py note add "New persistent piece of information"
    ```
    * Notes are stored in `.agent_memory/notes.json` and a limited number (last 10) are kept.

### Key `memory_cli.py` Commands

The `memory_cli.py` script is your primary interface to this layer.

* **Memory Entries:**
    * `query`: Search and filter past memory entries.
        * `--last <N>`: Get the last N entries.
        * `--tags <tag1> <tag2>`: Filter by tags.
        * `--search "<term>"`: Search content of entries.
    * `add`: Add a new memory entry.
        * Requires `context`, `observation`, `reflection`. Optional `--tags`.
    * `prune`: Remove old memory entries (e.g., `--older-than <days>`, `--keep-last <N>`).
    * `summarize`: Summarize entries within a date range (requires `--since` and `--until`).

* **Tasks (`.agent_memory/tasks.json`):**
    * `task list`: Show all current tasks.
    * `task add "<description>"`: Add a new task.
    * `task update <id> --status <status> [--description "<new_desc>"]`: Update a task.
    * `task remove <id>`: Remove a task.

* **Notes (`.agent_memory/notes.json`):**
    * `note list`: Show all current notes.
    * `note add "<content>"`: Add a new note.
    * `note remove <id>`: Remove a note.

### Important Directory Structure

* `.agent_memory/`: Root directory for this layer.
    * `entries/`: Contains individual memory entry files (JSONL format, named by timestamp).
    * `schema.json`: The schema used to validate memory entries.
    * `tasks.json`: Stores your current task list in JSON format.
    * `notes.json`: Stores permanent notes in JSON format.

By consistently using this memory layer, AI agents will build a valuable, private knowledge base about the project, improving their effectiveness and collaboration over time.
