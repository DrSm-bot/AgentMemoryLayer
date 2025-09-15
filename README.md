# Agent Memory Layer

This directory (`.agent_memory/`) contains a self-contained system for providing AI agents with a persistent memory layer, task tracking, and note-keeping capabilities within your project.

## Overview

The Agent Memory Layer allows AI agents to:
* **Log their activities:** Create timestamped entries about tasks performed, observations, and reflections.
* **Maintain context:** Query past entries to understand previous work and project-specific details.
* **Track tasks:** Manage a simple to-do list with statuses.
* **Store persistent notes:** Keep important, reusable information readily accessible.

This helps agents "learn" about your project over time, improving their effectiveness and enabling better collaboration if multiple agents (or an agent across multiple sessions) work on the same repository.

## Quick Start Guide 🚀

1.  **Copy to Your Repository:**
    * Copy the entire `.agent_memory` folder (including this `README.md`, `memory_cli.py`, `schema.json`, and the empty `entries/`, `tasks.json`, and `notes.json` files) into the root of your project repository.

2.  **Install Dependencies:**
    * From your project root, install the required Python packages:

      ```bash
      python -m pip install -r requirements.txt
      ```

3.  **Create or Update `AGENTS.md`:**
    * You should have an `AGENTS.md` file (or a similarly named file) in the root of your repository that serves as the primary guide for AI agents interacting with your project.
    * Copy the "Agent Memory Layer" section from the [provided generic AGENTS.md template](AGENTS.md) into your project's `AGENTS.md`.
    * **Crucially, customize the introductory parts of your `AGENTS.md`** to be specific to your project (e.g., replace `[Your Project Name]` with your actual project name). The Agent Memory Layer section itself is designed to be mostly generic.

4.  **Agent Interaction:**
    * Instruct your AI agents to refer to the `AGENTS.md` file in your repository for guidelines on how to use the memory layer.
    * The primary interaction point is the `memory_cli.py` script located within this `.agent_memory` directory.

## How It Works

The core components are:

* **`memory_cli.py`**: A Python command-line interface for agents to add, query, and manage memory entries, tasks, and notes.
* **`entries/`**: A directory where individual memory logs are stored as timestamped JSONL files.
* **`tasks.json`**: A JSON file storing the list of tasks.
* **`notes.json`**: A JSON file storing persistent notes.
* **`schema.json`**: A JSON schema that defines the structure of memory entries, ensuring consistency.

### For Agents: Using `memory_cli.py`

Refer to the "Agent Guide: Using the Agent Memory Layer" section in your project's root `AGENTS.md` file for detailed commands and workflow.

**Common workflow:**
1.  **Before starting a task:**
    * Query recent memory: `python .agent_memory/memory_cli.py query --last 5`
    * List tasks: `python .agent_memory/memory_cli.py task list`
    * List notes: `python .agent_memory/memory_cli.py note list`
2.  **After completing a task:**
    * Add memory entry: `python .agent_memory/memory_cli.py add "Context" "Observation" "Reflection" --tags "example" --task-id <task_id>`
    * Update task status: `python .agent_memory/memory_cli.py task update <id> --status "finished"`
    * Add notes if needed: `python .agent_memory/memory_cli.py note add "Useful persistent info"`

## Customization

* **`schema.json`**: You can extend the schema for memory entries if you need agents to log additional structured information. Ensure `memory_cli.py` is updated to handle any changes.
* **`memory_cli.py`**: The script can be modified to add more sophisticated querying, summarization, or integration with other project tools.
* **`AGENTS.md`**: Tailor the main `AGENTS.md` in your project root to provide specific context or instructions relevant to how agents should use their memory in *your* project.

## Dependencies

The Agent Memory Layer relies on a small set of Python packages beyond the standard library:

* [`jsonschema` (>=4.0,<5)](https://pypi.org/project/jsonschema/) – validates memory entries against `schema.json` before they are persisted.
* [`pytest`](https://pypi.org/project/pytest/) – optional, used when running the automated tests in `.agent_memory/tests/`.

Install the runtime dependencies with:

```bash
python -m pip install -r requirements.txt
```

If you plan to run the test suite, also install `pytest` (for example, `python -m pip install pytest`).
