from fastapi import FastAPI
from pydantic import BaseModel
from utils.matching import match_user_to_competences, recommend_jobs
from models.scoring import compute_block_scores

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
