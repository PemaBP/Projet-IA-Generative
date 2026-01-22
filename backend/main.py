from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
from dotenv import load_dotenv
load_dotenv()
 
from backend.models.MedEmbed_model import embed
from backend.utils.preprocessing import clean_text
from backend.utils.generative import generate_job_fiche
from backend.utils.matching import (
    score_competencies,
    score_blocks,
    score_jobs,
)
 
app = FastAPI(
    title="AISCA Backend",
    description="API d'analyse de profil et de matching métiers santé (MedEmbed)",
    version="1.0.0",
)
 
# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Charger le référentiel pour récupérer les titres de métiers, blocs, etc.
BASE_DIR = Path(__file__).resolve().parent
REF_PATH = BASE_DIR / "data" / "referentiel_jobs.json"
 
with open(REF_PATH, "r", encoding="utf-8") as f:
    REFERENTIEL = json.load(f)
 
 
# ====== SCHEMA D'ENTRÉE UTILISATEUR ======
 
class UserProfile(BaseModel):
    skills: str        # "Décrivez vos compétences clés"
    experiences: str   # "Détaillez vos expériences professionnelles"
    interests: str    # "Quelles sont vos appétences ?"
 
 
# ====== ENDPOINT DE TEST ======
@app.get("/")
def root():
    return {"message": "AISCA backend is running 🚀"}
 
 
# ====== ENDPOINT PRINCIPAL : MATCHING PROFIL → MÉTIERS ======
@app.post("/match_profile")
def match_profile(payload: UserProfile):
    """
    Prend le texte user (compétences, expériences, appétences),
    calcule l'embedding MedEmbed, puis :
      - scores par compétence
      - scores par blocs
      - scores par métiers (avec top 5)
    """
 
    # 1. Fusion + nettoyage du texte utilisateur
    full_text = " ".join([
        payload.skills or "",
        payload.experiences or "",
        payload.interests or "",
    ])
    full_text = clean_text(full_text)
 
    # 2. Embedding utilisateur via MedEmbed (normalisation déjà gérée dans embed)
    user_emb = embed(full_text, normalize=True)
 
    # 3. Scoring
    competence_scores = score_competencies(user_emb)
    block_scores = score_blocks(competence_scores)
    job_scores = score_jobs(block_scores)
 
    # 4. Trier les blocs par score
    sorted_blocks = sorted(block_scores.items(), key=lambda x: x[1], reverse=True)
 
    # 5. Trier les métiers par score
    sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)
 
    # 6. Récupérer les infos métiers (titre) pour le top 5
    jobs_by_id = {j["job_id"]: j for j in REFERENTIEL["jobs"]}
 
    top_jobs = []
    for job_id, score in sorted_jobs[:5]:
        meta = jobs_by_id.get(job_id, {})
        top_jobs.append({
            "job_id": job_id,
            "title": meta.get("title", "Inconnu"),
            "score": round(float(score), 3),
        })
 
    # 7. Renvoyer un truc bien structuré pour ton front / debug
    return {
        "scores_par_blocs": {
            bid: round(float(s), 3) for bid, s in sorted_blocks
        },
        "top_metiers": top_jobs,
    }
@app.post("/analyze")
def analyze(payload: UserProfile):
    """
    Version simplifiée pour le front : renvoie uniquement
    - embedding utilisateur
    - scores compétences
    - scores blocs
    - scores métiers
    """
    
    # 1. Fusion + nettoyage
    full_text = " ".join([
        payload.skills or "",
        payload.experiences or "",
        payload.interests or "",
    ])
    full_text = clean_text(full_text)

    # 2. Embedding
    user_emb = embed(full_text, normalize=True)

    # 3. Scoring
    competence_scores = score_competencies(user_emb)
    block_scores = score_blocks(competence_scores)
    job_scores = score_jobs(block_scores)

    #Trie des métiers
    sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)
    jobs_by_id = {j["job_id"]: j for j in REFERENTIEL["jobs"]}

    top_job_id,top_score=sorted_jobs[0]
    top_job_title=jobs_by_id.get(top_job_id,{}).get("title","Métier inconnu")

    try:
        job_fiche = generate_job_fiche(
            job_title=top_job_title,
            profile_summary=full_text
        )
    except Exception as e:
        job_fiche = f"Erreur génération IA : {str(e)}"

    return {
    "embedding": user_emb.tolist(),
    "competence_scores": competence_scores,
    "block_scores": block_scores,
    "job_scores": job_scores,
    "top_job": {
            "job_id": top_job_id,
            "title": top_job_title,
            "score": round(float(top_score), 3),
        },
        "job_fiche_ai": job_fiche,
    }