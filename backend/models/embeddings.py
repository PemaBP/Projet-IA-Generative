import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

REF_PATH = Path(__file__).resolve().parents[1] / "data" / "referentiel_jobs.json"

with open(REF_PATH, "r", encoding="utf-8") as f:
    REFERENTIEL = json.load(f)

def load_reference_embeddings():
    texts = [c["text"] for c in REFERENTIEL["competencies"]]
    emb = MODEL.encode(texts, normalize_embeddings=True)
    return emb

REFERENCE_EMBEDDINGS = load_reference_embeddings()