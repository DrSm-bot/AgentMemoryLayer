import logging
from pathlib import Path
import importlib.util

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


manage_tasks = _load_module("manage_tasks")
manage_notes = _load_module("manage_notes")


@pytest.mark.parametrize(
    "loader, filename",
    [
        (manage_tasks.load_tasks, "tasks.json"),
        (manage_notes.load_notes, "notes.json"),
    ],
)
def test_load_with_corrupted_json_returns_empty_list_and_logs_warning(loader, filename, tmp_path, caplog):
    file_path = tmp_path / filename
    file_path.write_text("{", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        result = loader(file_path)

    assert result == []
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.WARNING
    assert "Failed to decode JSON" in record.getMessage()
    assert str(file_path) in record.getMessage()
