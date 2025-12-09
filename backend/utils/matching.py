# backend/utils/matching.py
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import clean_text
from ..models.embeddings import REFERENTIEL, REFERENCE_EMBEDDINGS
from ..models.sbert_model import embed_one


def embed_user_text(text: str):
    text = clean_text(text)
    return embed_one(text, normalize=True)


def match_user_to_competences(full_text: str):
    user_emb = embed_user_text(full_text)
    sims = cosine_similarity([user_emb], REFERENCE_EMBEDDINGS)[0]

    results = []
    for comp, score in zip(REFERENTIEL["competencies"], sims):
        results.append({
            "competency_id": comp["competency_id"],
            "label": comp["text"],
            "block_id": comp["block_id"],
            "similarity": float(score)
        })

    return results


def recommend_jobs(comp_scores):
    job_scores = []
    for job in REFERENTIEL["jobs"]:
        req = job["required_competencies"]
        relevant = [c for c in comp_scores if c["competency_id"] in req]

        if relevant:
            avg = sum(r["similarity"] for r in relevant) / len(relevant)
        else:
            avg = 0.0

        job_scores.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "score": round(float(avg), 3)
        })

    job_scores.sort(key=lambda x: x["score"], reverse=True)
    return job_scores[:5]
