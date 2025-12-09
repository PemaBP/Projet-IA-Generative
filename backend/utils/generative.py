from openai import OpenAI
client = OpenAI()

def generate_job_fiche(job_title, profile_summary):
    prompt = f"""
    Génère une fiche métier pour un(e) étudiant(e) en médecine :
    Métier : {job_title}
    Profil : {profile_summary}

    Contenu attendu :
    - Missions
    - Compétences clés
    - Compétences manquantes (à partir du profil)
    - Parcours recommandé
    - Fourchette de salaire
    - Feuille de route mois par mois sur 12 mois
    """
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message["content"]
