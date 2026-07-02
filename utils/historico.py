import json
import os
from datetime import datetime

_PATH = os.path.join(os.path.dirname(__file__), "..", "historico.json")
MAX_ENTRIES = 200


def registrar(modulo: str, status: str, detalhes: str = "") -> None:
    entries = listar(MAX_ENTRIES)
    entries.insert(0, {
        "modulo": modulo,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "detalhes": detalhes,
    })
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(entries[:MAX_ENTRIES], f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def listar(n: int = 30) -> list:
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return json.load(f)[:n]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def ultima(modulo: str) -> dict | None:
    for entry in listar(MAX_ENTRIES):
        if entry.get("modulo") == modulo:
            return entry
    return None
