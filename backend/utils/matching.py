import numpy as np
import json
import os 
# Charger referentiel

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, "data", "referentiel_jobs.json"), "r", encoding="utf-8") as f:

    REFERENTIEL = json.load(f)
 
competencies = REFERENTIEL["competencies"]

jobs = REFERENTIEL["jobs"]

blocks = REFERENTIEL["competency_blocks"]
 
# Charger embeddings pré-calculés

from backend.models.embeddings import REFERENCE_EMBEDDINGS

from backend.models.MedEmbed_model import embed
 
 
def cosine(a, b):

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
 
 
def score_competencies(user_emb):

    scores = {}

    for i, c in enumerate(competencies):

        comp_id = c["competency_id"]

        scores[comp_id] = cosine(user_emb, REFERENCE_EMBEDDINGS[i])

    return scores
 
 
def score_blocks(comp_scores):

    block_scores = {}
 
    for c in competencies:

        cid = c["competency_id"]

        bid = c["block_id"]

        sc = comp_scores[cid]
 
        block_scores.setdefault(bid, []).append(sc)
 
    # moyenne pondérée (améliore cohérence)

    return {

        bid: float(np.mean(vals) * (1 + 0.1 * len(vals)))

        for bid, vals in block_scores.items()

    }
 
 
def score_jobs(block_scores):

    job_scores = {}
 
    for j in jobs:

        scores = []

        for cid in j["required_competencies"]:

            block_id = next(c["block_id"] for c in competencies if c["competency_id"] == cid)

            scores.append(block_scores.get(block_id, 0))
 
        # new formula : moyenne *et* max → boost intelligence

        job_scores[j["job_id"]] = float(0.7 * np.mean(scores) + 0.3 * np.max(scores))
 
    return job_scores