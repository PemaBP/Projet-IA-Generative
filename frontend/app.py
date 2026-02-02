import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="AISCA - Orientation Médecine", layout="wide")

def _markdown_to_basic_text(md: str) -> str:
    """Conversion ultra simple Markdown -> texte lisible pour PDF."""
    text = md or ""
    text = re.sub(r"`{1,3}.*?`{1,3}", "", text, flags=re.DOTALL)   # enlève blocs inline/code
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)                   # enlève images
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)               # liens -> texte
    text = re.sub(r"[*_>#-]", " ", text)                          # symboles md
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def build_pdf_bytes(title: str, content_md: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    text = _markdown_to_basic_text(content_md)
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        story.append(Paragraph(para.replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    return buffer.getvalue()

# -----------------------
# Helpers : état & navigation
# -----------------------
if "step" not in st.session_state:
    st.session_state.step = 0  # 0 = welcome, 1 = infos, 2 = formulaire+résultats

def go_to(step: int):
    st.session_state.step = step

# -----------------------
# (Optionnel) Charger référentiel pour noms des blocs
# -----------------------
BLOCKS_BY_ID = {}
try:
    ref_path = Path(__file__).resolve().parents[1] / "backend" / "data" / "referentiel_jobs.json"
    with open(ref_path, "r", encoding="utf-8") as f:
        ref = json.load(f)
    BLOCKS_BY_ID = {b["block_id"]: b for b in ref.get("competency_blocks", [])}
except Exception:
    BLOCKS_BY_ID = {}

# =======================
# STEP 0 — Welcome
# =======================
if st.session_state.step == 0:
    st.title("Bienvenue sur AISCA ")

    st.markdown(
    """
AISCA t’aide à transformer tes compétences, expériences et centres d’intérêt en  **recommandations de métiers personnalisées**, puis en **fiches métiers détaillées** dans le domaine de la **santé**.""")

    st.image("./backend/data/photo_medecins.jpg", width=800)
    st.markdown(
    """
**AISCA est un projet développé par _Péma_ et _Aurélien_**, étudiants à l’EFREI Paris,  
dans le cadre d’un travail autour de l’IA, du matching de compétences  
et de l’orientation en santé.
"""
    )


    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("Objectif : te donner une direction claire, sans te perdre dans 40 spécialités.")
    with col2:
        st.success("Let’s go : 2 minutes de formulaire et on s'occupe du reste !")

    st.button("Commencer", on_click=go_to, args=(1,))

# =======================
# STEP 1 — Infos perso
# =======================
elif st.session_state.step == 1:
    st.title("Décris-toi brièvement")

    # Valeurs par défaut si déjà rempli
    prenom = st.text_input("Prénom", value=st.session_state.get("prenom", ""))
    age = st.number_input("Âge", min_value=10, max_value=90, value=int(st.session_state.get("age", 23)))
    niveau = st.selectbox(
        "Niveau d’étude",
        options=["PACES/LAS", "DFGSM2", "DFGSM3", "DFASM1", "DFASM2", "DFASM3", "Interne", "Autre"],
        index=0 if "niveau" not in st.session_state else ["PACES/LAS","DFGSM2","DFGSM3","DFASM1","DFASM2","DFASM3","Interne","Autre"].index(st.session_state["niveau"])
    )
    etab = st.text_input("Établissement universitaire", value=st.session_state.get("etablissement", ""))

    colA, colB = st.columns([1, 1])
    with colA:
        st.button("⬅️ Retour", on_click=go_to, args=(0,))
    with colB:
        # Validation minimaliste
        can_continue = bool(prenom.strip()) and bool(etab.strip())
        if st.button("Passer à l’étape suivante ➜", disabled=not can_continue):
            st.session_state["prenom"] = prenom.strip()
            st.session_state["age"] = int(age)
            st.session_state["niveau"] = niveau
            st.session_state["etablissement"] = etab.strip()
            go_to(2)

        if not can_continue:
            st.caption("⚠️ Mets au moins ton prénom + ton établissement pour continuer.")

# =======================
# STEP 2 — Ton formulaire existant + résultats
# =======================
else:
    prenom = st.session_state.get("prenom", "toi")
    age = st.session_state.get("age", "")
    niveau = st.session_state.get("niveau", "")
    etab = st.session_state.get("etablissement", "")

    st.title(f"AISCA 🩺 — Bonjour {prenom} !")

    st.markdown(
        f"""
**Profil :** {prenom} — {age} ans — {niveau} — {etab}  
Passons à la partie où tu nous donnes plus de détails sur toi dans le domaine de la santé !
"""
    )

    colA, colB = st.columns([1, 1])
    with colA:
        st.button("⬅ Modifier mes infos", on_click=go_to, args=(1,))
    with colB:
        if st.button("🧹 Réinitialiser l’analyse"):
            st.session_state.pop("analysis", None)
            st.success("Analyse réinitialisée.")

    st.subheader("📝 Formulaire")
    domain = st.multiselect("Sélectionnez votre domaine d'étude", ["Médecine"])

    st.info("Si vous souhaitez obtenir un résultat pertinent et précis, soyeux clair et détaillé dans vos réponses.")

    skills = st.text_area("Décrivez vos compétences clés *")
    exp = st.text_area("Détaillez vos expériences professionnelles *")
    interests = st.text_area("Quelles sont vos appétences ? *")

    st.subheader("Informations compléméntaires")

    relation_patient = st.radio(
        "Quel type de relation au patient te correspond le plus ?",
        [
            "Peu de contact patient",
            "Suivi régulier et individualisé",
            "Contact intense et varié"
        ]
    )

    mouvement = st.radio(
        "Souhaites-tu travailler principalement sur le mouvement et la fonction corporelle ?",
        [
            "Non",
            "En partie",
            "Oui, c’est central"
        ]
    )

    type_activite = st.radio(
        "Quel type d’activité te motive le plus ?",
        [
            "Activité manuelle et pratique",
            "Analyse / raisonnement / données",
            "Un mélange des deux"
        ]
    )

    # ✅ Validation : champs texte obligatoires
    can_analyze = bool(skills.strip()) and bool(exp.strip()) and bool(interests.strip())

    if not can_analyze:
        st.caption("⚠️ Les trois champs de texte libre (compétences, expériences, appétences) sont obligatoires pour lancer l’analyse.")


    # On construit le profil complet une seule fois
    full_text = " ".join([skills, exp, interests]).strip()

    

    # -----------------------
    # Analyse du profil
    # -----------------------
    if st.button("Analyser mon profil ", disabled=not can_analyze):
        if not can_analyze:
            st.warning("Remplis tous les champs texte pour lancer l’analyse.")
        else:
            user_payload = {
                "skills": skills,
                "experiences": exp,
                "interests": interests,
                "relation_patient": relation_patient,
                "mouvement": mouvement,
                "type_activite": type_activite,
            }

        try:
            response = requests.post(f"{BACKEND_URL}/analyze", json=user_payload, timeout=60)

            if response.status_code == 200:
                st.session_state["analysis"] = response.json()
                st.success(f"Analyse réussie {prenom}. Fais défiler pour voir les résultats.")
            else:
                st.error(f"Erreur lors de l'analyse (code {response.status_code}).")

        except Exception as e:
            st.error(
                "Impossible de contacter le backend \n"
                "Vérifie que FastAPI tourne.\n\n"
                f"Détail : {e}"
            )

    # -----------------------
    # Affichage des résultats
    # -----------------------
    if "analysis" in st.session_state:
        result = st.session_state["analysis"]

        st.header("Résultats de l'analyse")

        # Scores par blocs
        st.subheader("Scores par blocs")
        block_scores = result.get("block_scores", {})
        if block_scores:
            rows = []
            for bid, score in block_scores.items():
                bname = BLOCKS_BY_ID.get(bid, {}).get("name", bid)
                rows.append({"Bloc": bname , "Score": float(score)})

            df_blocks = pd.DataFrame(rows).sort_values("Score", ascending=False).head(3)
            st.dataframe(df_blocks, width="stretch")
        else:
            st.warning("Aucun score de bloc retourné par le backend.")

        # Top jobs détaillés si ton backend renvoie top_jobs (recommandé)
        top_jobs = result.get("top_jobs", [])

        st.divider()
        st.subheader(f"Top métiers recommandés pour {prenom}")

        import numpy as np


        if not top_jobs:
            st.warning("Le backend n'a pas renvoyé de Top 3 (champ 'top_jobs').")
        else:
            raw_scores = [j.get("job_score", 0.0) for j in top_jobs]
            max_score = max(raw_scores) if raw_scores else 1.0

            top_rows = []
            for j in top_jobs:
                raw_score = j.get("job_score", 0.0)
                percent_score = (raw_score / max_score) if max_score > 0 else 0.0

                top_rows.append({
                    "Métier": j.get("title", "Métier inconnu"),
                    "Score": round(percent_score, 1)
                })

            st.dataframe(pd.DataFrame(top_rows), width="stretch")

            # --- Détail par métier ---
            for j in top_jobs:
                title = j.get("title", "Métier inconnu")
                raw_score = j.get("job_score", 0.0)
                comps = j.get("competencies", [])

                with st.expander(f"Compétences associées — {title} (score {raw_score})"):
                    if comps:
                        df_comps = pd.DataFrame(comps)
                        cols = [c for c in ["competency_id", "text", "block_name", "block_id", "user_score"] if c in df_comps.columns]
                        st.dataframe(df_comps[cols], width="stretch")
                    else:
                        st.info("Aucune compétence détaillée renvoyée pour ce métier.")

                # Exemple : top 3 compétences du métier
                    top_comps = comps[:3]

                    labels = [c["text"] for c in top_comps]
                    values = [c["user_score"] for c in top_comps]

                    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                    values += values[:1]
                    angles += angles[:1]

                    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
                    ax.plot(angles, values, linewidth=2)
                    ax.fill(angles, values, alpha=0.25)
                    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
                    ax.set_ylim(0, 1)

                    col_left, col_center, col_right = st.columns([1, 2, 1])

                    with col_center:
                        st.pyplot(fig)

            st.divider()
            st.subheader("Générer une fiche métier")

            top_titles = [j.get("title", "Métier inconnu") for j in top_jobs]
            selected_job = st.radio("Choisis un métier parmi ton top 3", options=top_titles)

            if st.button("Générer la fiche métier"):
                if not full_text:
                    st.warning("Remplis au moins un champ (compétences / expériences / intérêts) pour générer une fiche.")
                else:
                    with st.spinner("Gemini forge ta fiche..."):
                        resp = requests.post(
                            f"{BACKEND_URL}/generate_fiche",
                            json={"job_title": selected_job, "profile": full_text},
                            timeout=120,
                        )

                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Fiche disponible !  Courage {prenom}, tu peux le faire (de la part de la team AISCA).")
                        st.markdown(data.get("content", ""))
                        fiche_text = data.get("content", "")
                        pdf_bytes = build_pdf_bytes(
                            title=f"Fiche métier — {selected_job}",
                            content_md=fiche_text
                        )

                        st.download_button(
                            label="Télécharger la fiche en PDF",
                            data=pdf_bytes,
                            file_name=f"fiche_metier_{selected_job.lower().replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error(f"Erreur backend lors de la génération (code {resp.status_code}).")
    else:
        st.info("Lance une analyse pour voir tes résultats.")
