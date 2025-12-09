import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from pydantic import BaseModel
from backend.utils.matching import match_user_to_competences, recommend_jobs
from backend.models.scoring import compute_block_scores
from backend.utils.generative import generate_job_fiche


app = FastAPI()

class UserInput(BaseModel):
    skills: str
    experiences: str
    interests: str

@app.post("/analyze")
def analyze(user: UserInput):

    full_text = " ".join([user.skills, user.experiences, user.interests])

    comp_scores = match_user_to_competences(full_text)
    block_scores = compute_block_scores(comp_scores)
    jobs = recommend_jobs(comp_scores)

    return {
        "competency_scores": comp_scores,
        "block_scores": block_scores,
        "jobs": jobs
    }

class GenRequest(BaseModel):
    job_title: str
    profile: str

@app.post("/generate_fiche")
def generate_fiche(req: GenRequest):
    content = generate_job_fiche(req.job_title, req.profile)
    return {"content": content}
