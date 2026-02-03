import os

import google.generativeai as genai
from backend.utils.fiche_cache import get_cached_fiche, save_fiche

from dotenv import load_dotenv

load_dotenv()



# Configuration Gemini

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Déclaration du modèle
model = genai.GenerativeModel("gemini-2.5-flash")


# Génération fiche métier

def generate_job_fiche(job_title: str, profile_summary: str) -> str:
    # 1) Vérifier le cache
    cached = get_cached_fiche(job_title)
    if cached:
        return cached

    # 2) Prompt Gemini
    prompt = f"""
Tu dois générer une fiche métier UNIQUEMENT pour le métier suivant : {job_title}.
Ne recommande pas d’autres métiers.
Ne propose pas d’alternatives.

Profil utilisateur :
{profile_summary}

Contenu attendu :
- Missions
- Compétences clés
- Compétences manquantes (en fonction du profil)
- Parcours recommandé
- Fourchette de salaire
- Feuille de route mois par mois sur 12 mois

Réponds de manière structurée, claire et professionnelle.
"""

    # 3) Appel Gemini
    response = model.generate_content(prompt)
    text = response.text

    # 4) Sauvegarde cache
    save_fiche(job_title, text)

    return text
