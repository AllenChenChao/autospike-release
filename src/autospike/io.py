from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_signal_csv(path: str | Path) -> list[float]:
    path = Path(path)
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            rows.append([float(value) for value in row if value.strip()])

    if not rows:
        raise ValueError("CSV input must not be empty")
    if len(rows) == 1:
        return rows[0]
    if all(len(row) == 1 for row in rows):
        return [row[0] for row in rows]
    raise ValueError("CSV input must be one numeric column or one numeric row")


def save_array_csv(values: Any, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if isinstance(values, (int, float)):
            writer.writerow([values])
        else:
            for item in values:
                if isinstance(item, (list, tuple)):
                    writer.writerow(item)
                else:
                    writer.writerow([item])
    return path


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        numeric = float(value)
        if numeric == float("inf"):
            return "inf"
        if numeric == float("-inf"):
            return "-inf"
        if numeric != numeric:
            return "nan"
        return numeric
    if isinstance(value, int):
        return int(value)
    return value


def save_json(data: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(_json_ready(data), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def save_metadata_csv(rows: list[dict[str, Any]], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("metadata rows must not be empty")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path
