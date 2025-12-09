import json
from pathlib import Path
from .sbert_model import embed_many

REF_PATH = Path(__file__).resolve().parents[1] / "data" / "referentiel_jobs.json"

with open(REF_PATH, "r", encoding="utf-8") as f:
    REFERENTIEL = json.load(f)

def load_reference_embeddings():
    texts = [c["text"] for c in REFERENTIEL["competencies"]]
    emb = embed_many(texts, normalize=True)
    return emb

REFERENCE_EMBEDDINGS = load_reference_embeddings()
