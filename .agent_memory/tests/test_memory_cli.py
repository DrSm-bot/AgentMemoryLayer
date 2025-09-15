import json
import shutil
from pathlib import Path

import pytest

# Import modules
import importlib.util

root = Path(__file__).resolve().parents[1]
spec_cli = importlib.util.spec_from_file_location('memory_cli', root / 'memory_cli.py')
memory_cli = importlib.util.module_from_spec(spec_cli)
spec_cli.loader.exec_module(memory_cli)

SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'schema.json'

with SCHEMA_PATH.open() as f:
    SCHEMA = json.load(f)

try:
    from jsonschema import validate
except Exception:  # pragma: no cover
    validate = None

@pytest.mark.skipif(validate is None, reason="jsonschema not installed")
def test_schema_optional_task_id():
    base = {
        "ts": "2025-05-27T00:00:00",
        "agent": "test",
        "run_id": "1",
        "context": "ctx",
        "observation": "obs",
        "reflection": "refl",
        "tags": [],
    }
    # should validate without task_id
    validate(instance=base, schema=SCHEMA)
    base["task_id"] = "abc"
    validate(instance=base, schema=SCHEMA)

@pytest.mark.skipif(validate is None, reason="jsonschema not installed")
def test_cli_add_with_and_without_task_id(tmp_path):
    memory_dir = tmp_path
    shutil.copy(SCHEMA_PATH, memory_dir / 'schema.json')

    memory_cli.main([
        'add', 'ctx', 'obs', 'refl', '--task-id', 'tid', '--memory-dir', str(memory_dir)
    ])
    files = list((memory_dir / 'entries').glob('*.jsonl'))
    assert len(files) == 1
    with files[0].open() as f:
        entry = json.loads(f.readline())
    assert entry['task_id'] == 'tid'

    memory_cli.main([
        'add', 'ctx2', 'obs2', 'refl2', '--memory-dir', str(memory_dir)
    ])
    files = sorted((memory_dir / 'entries').glob('*.jsonl'))
    assert len(files) == 2
    with files[1].open() as f:
        entry = json.loads(f.readline())
    assert 'task_id' not in entry
