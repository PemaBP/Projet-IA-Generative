from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from .preprocessing import clean_text
from ..models.embeddings import REFERENTIEL, REFERENCE_EMBEDDINGS

MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def embed_user_text(text):
    text = clean_text(text)
    return MODEL.encode([text], normalize_embeddings=True)[0]

def match_user_to_competences(full_text):
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
    
<<<<<<< HEAD
    return results
=======
    return results

def recommend_jobs(comp_scores):
    job_scores = []
    for job in REFERENTIEL["jobs"]:
        req = job["required_competencies"]
        relevant = [c for c in comp_scores if c["competency_id"] in req]

        if relevant:
            avg = sum(r["similarity"] for r in relevant) / len(relevant)
        else:
            avg = 0

        job_scores.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "score": round(float(avg), 3)
        })

    job_scores.sort(key=lambda x: x["score"], reverse=True)
    return job_scores[:5]
>>>>>>> develop
