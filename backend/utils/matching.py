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
    
    return results