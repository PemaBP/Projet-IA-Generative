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
    st.title("Bienvenue sur AISCA 🩺✨")

    st.markdown(
    """
AISCA t’aide à transformer tes compétences, expériences et centres d’intérêt en  
**recommandations de métiers personnalisées**, puis en **fiches métiers détaillées**.


🧠 **AISCA est un projet développé par _Péma_ et _Aurélien_**,  
dans le cadre d’un travail autour de l’IA, du matching de compétences  
et de l’orientation en santé.
"""
)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("Objectif : te donner une direction claire, sans te perdre dans 40 spécialités.")
    with col2:
        st.success("Let’s go : 2 minutes de formulaire, et on lance la machine 🧠")

    st.button("Commencer", on_click=go_to, args=(1,))

# =======================
# STEP 1 — Infos perso
# =======================
elif st.session_state.step == 1:
    st.title("Qui es-tu (version administrative, mais sympa) ? 🪪")

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

    st.title(f"AISCA 🩺 — Hello {prenom} !")

    st.markdown(
        f"""
**Profil :** {prenom} — {age} ans — {niveau} — {etab}  
Bon, maintenant on passe à la partie où tu balances tes skills et AISCA fait le tri ✨
"""
    )

    colA, colB = st.columns([1, 1])
    with colA:
        st.button("⬅️ Modifier mes infos", on_click=go_to, args=(1,))
    with colB:
        if st.button("🧹 Réinitialiser l’analyse"):
            st.session_state.pop("analysis", None)
            st.success("Analyse réinitialisée.")

    st.subheader("📝 Formulaire")
    domain = st.multiselect("Sélectionnez votre domaine d'activité", ["Médecine"])

    skills = st.text_area("Décrivez vos compétences clés")
    exp = st.text_area("Détaillez vos expériences professionnelles")
    interests = st.text_area("Quelles sont vos appétences ?")

    # On construit le profil complet une seule fois
    full_text = " ".join([skills, exp, interests]).strip()

    # -----------------------
    # Analyse du profil
    # -----------------------
    if st.button("Analyser mon profil 🧠"):
        user_payload = {
            "skills": skills,
            "experiences": exp,
            "interests": interests,
        }

        try:
            response = requests.post(f"{BACKEND_URL}/analyze", json=user_payload, timeout=60)

            if response.status_code == 200:
                st.session_state["analysis"] = response.json()
                st.success(f"Analyse réussie {prenom} ✅ Fais défiler pour voir les résultats.")
            else:
                st.error(f"Erreur lors de l'analyse (code {response.status_code}).")

        except Exception as e:
            st.error(
                "Impossible de contacter le backend 😭\n"
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
                rows.append({"Bloc": f"{bname} ({bid})", "Score": float(score)})

            df_blocks = pd.DataFrame(rows).sort_values("Score", ascending=False)
            st.dataframe(df_blocks, use_container_width=True)
        else:
            st.warning("Aucun score de bloc retourné par le backend.")

        # Graph blocs
        if block_scores:
            df_plot = pd.DataFrame(list(block_scores.items()), columns=["Bloc", "Score"])
            fig, ax = plt.subplots()
            ax.bar(df_plot["Bloc"], df_plot["Score"])
            ax.set_ylabel("Score")
            ax.set_title("Scores par Bloc")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

        # Top jobs détaillés si ton backend renvoie top_jobs (recommandé)
        top_jobs = result.get("top_jobs", [])

        st.divider()
        st.subheader(f"Top métiers recommandés pour {prenom}")

        if not top_jobs:
            st.warning("Le backend n'a pas renvoyé de Top 3 (champ 'top_jobs').")
        else:
            top_rows = [{"Métier": j.get("title", "Métier inconnu"), "Score": j.get("job_score", 0.0)} for j in top_jobs]
            st.dataframe(pd.DataFrame(top_rows), use_container_width=True)

            for j in top_jobs:
                title = j.get("title", "Métier inconnu")
                score = j.get("job_score", 0.0)
                comps = j.get("competencies", [])

                with st.expander(f"Compétences associées — {title} (score {score})"):
                    if comps:
                        df_comps = pd.DataFrame(comps)
                        cols = [c for c in ["competency_id", "text", "block_name", "block_id", "user_score"] if c in df_comps.columns]
                        st.dataframe(df_comps[cols], use_container_width=True)
                    else:
                        st.info("Aucune compétence détaillée renvoyée pour ce métier.")

            st.divider()
            st.subheader("✨ Générer une fiche métier (Gemini)")

            top_titles = [j.get("title", "Métier inconnu") for j in top_jobs]
            selected_job = st.radio("Choisis un métier parmi ton Top 3", options=top_titles)

            if st.button("Générer la fiche métier (Gemini)"):
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
                        st.success(f"Fiche disponible ✅ Courage {prenom}, c’est du solide.")
                        st.markdown(data.get("content", ""))
                        fiche_text = data.get("content", "")
                        pdf_bytes = build_pdf_bytes(
                            title=f"Fiche métier — {selected_job}",
                            content_md=fiche_text
                        )

                        st.download_button(
                            label="📄 Télécharger la fiche en PDF",
                            data=pdf_bytes,
                            file_name=f"fiche_metier_{selected_job.lower().replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error(f"Erreur backend lors de la génération (code {resp.status_code}).")
    else:
        st.info("Lance une analyse pour voir tes résultats.")
