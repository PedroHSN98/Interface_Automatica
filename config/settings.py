import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

DEFAULTS = {
    "theme": "dark",
    "scraper_links": "fontes/links.txt",
    "scraper_output": "galeria_noticias",
    "scraper_agendado": False,
    "scraper_horario": "08:00",
    "ama_urls": "urls.txt",
    "ama_result": "resultado.xlsx",
    "ama_threshold": 5.0,
    "notificacoes": True,
    "logs_servidores_elastic": ["Elasticsearch 1", "Elasticsearch 2", "Elasticsearch 3"],
    "logs_servidores_liferay": ["Liferay 1", "Liferay 2"],
}


def load() -> dict:
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULTS, **data}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULTS)


def save(cfg: dict) -> None:
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get(key: str, default=None):
    return load().get(key, DEFAULTS.get(key, default))


def set_key(key: str, value) -> None:
    cfg = load()
    cfg[key] = value
    save(cfg)
