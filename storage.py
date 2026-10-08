"""Guardado de los dos campos de ejemplo en un TXT local."""

import json
from pathlib import Path
from threading import Lock


_write_lock = Lock()


def save_record(file_path, visitante, referencia):
    record = json.dumps(
        {"visitante": visitante, "referencia": referencia},
        ensure_ascii=False,
    )
    path = Path(file_path)
    with _write_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as file:
            file.write(record + "\n")
