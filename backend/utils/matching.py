import numpy as np
import json
<<<<<<< HEAD
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
=======
import os

# Charger referentiel
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(BASE_DIR, "data", "referentiel_jobs.json"), "r", encoding="utf-8") as f:
    REFERENTIEL = json.load(f)

competencies = REFERENTIEL["competencies"]
jobs = REFERENTIEL["jobs"]
blocks = REFERENTIEL["competency_blocks"]

from collections import Counter
import math

# ===== Pondération IDF des compétences (rareté) =====
# combien de jobs demandent chaque compétence ?
freq = Counter(cid for j in jobs for cid in j.get("required_competencies", []))
N = len(jobs)

# poids > 1 pour les compétences rares
IDF = {
    cid: math.log((N + 1) / (freq[cid] + 1)) + 1.0
    for cid in freq
}

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
        sc = comp_scores.get(cid, 0.0)
        block_scores.setdefault(bid, []).append(sc)

    # ✅ Moyenne simple (évite d'écraser le ranking avec un boost artificiel)
    return {bid: float(np.mean(vals)) for bid, vals in block_scores.items()}


def score_jobs(comp_scores, k=4):
    job_scores = {}

    for j in jobs:
        req = j.get("required_competencies", [])
        if not req:
            job_scores[j["job_id"]] = 0.0
            continue

        weighted = []
        for cid in req:
            s = float(comp_scores.get(cid, 0.0))
            w = float(IDF.get(cid, 1.0))
            weighted.append(s * w)

        weighted.sort(reverse=True)
        topk = weighted[: min(k, len(weighted))]

        job_scores[j["job_id"]] = float(0.7 * np.mean(topk) + 0.3 * np.max(weighted))

    return job_scores
>>>>>>> 0e765017 (Initial clean commit)
