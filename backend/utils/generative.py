import google.generativeai as genai
import os

# Config API Gemini
genai.configure(api_key=os.getenv("AIzaSyB45lFwOb1IcLKefxs7w7rSIvnjvqs-4Bc"))

# Charger le modèle
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_job_fiche(job_title, profile_summary):
    prompt = f"""
    Génère une fiche métier pour un(e) étudiant(e) en médecine.
    
    Métier : {job_title}
    Profil : {profile_summary}

    Contenu attendu :
    - Missions
    - Compétences clés
    - Compétences manquantes (à partir du profil)
    - Parcours recommandé
    - Fourchette de salaire
    - Feuille de route mois par mois sur 12 mois

    Réponds de manière structurée et professionnelle.
    """

    response = model.generate_content(prompt)

    return response.text
