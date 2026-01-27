import json
from pathlib import Path

CACHE_PATH = Path(__file__).resolve().parents[1] / "data" / "fiche_cache.json"
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(cache: dict) -> None:
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

from typing import Optional

def get_cached_fiche(job_title: str) -> Optional[str]:
    cache = _load_cache()
    return cache.get(job_title)

def save_fiche(job_title: str, content: str) -> None:
    cache = _load_cache()
    cache[job_title] = content
    _save_cache(cache)
