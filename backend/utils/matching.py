import json
import os
import math
import numpy as np
from collections import Counter


# Chargement du référentiel

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

with open(
    os.path.join(BASE_DIR, "data", "referentiel_jobs.json"),
    "r",
    encoding="utf-8"
) as f:
    REFERENTIEL = json.load(f)

competencies = REFERENTIEL["competencies"]
jobs = REFERENTIEL["jobs"]
blocks = REFERENTIEL["competency_blocks"]


# compétences rares

freq = Counter(
    cid for j in jobs for cid in j.get("required_competencies", [])
)
N = len(jobs)

IDF = {
    cid: math.log((N + 1) / (freq[cid] + 1)) + 1.0
    for cid in freq
}


# Embeddings

from backend.models.embeddings import REFERENCE_EMBEDDINGS
from backend.models.MedEmbed_model import embed


def cosine(a, b):
    # embeddings déjà normalisés 
    return float(np.dot(a, b))



# 1. Score par compétence

def score_competencies(user_emb):
    scores = {}

    for i, c in enumerate(competencies):
        cid = c["competency_id"]
        scores[cid] = cosine(user_emb, REFERENCE_EMBEDDINGS[i])

    return scores



# 2. Score par bloc

def score_blocks(comp_scores):
    block_scores = {}

    for c in competencies:
        cid = c["competency_id"]
        bid = c["block_id"]
        sc = comp_scores.get(cid, 0.0)
        block_scores.setdefault(bid, []).append(sc)

    # moyenne simple (stable, interprétable)
    return {
        bid: float(np.mean(vals))
        for bid, vals in block_scores.items()
        if vals
    }



# 3. Score par métier

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

        # équilibre cohérent : compatibilité globale + pic fort
        job_scores[j["job_id"]] = float(
            0.7 * np.mean(topk) + 0.3 * max(weighted)
        )

    return job_scores