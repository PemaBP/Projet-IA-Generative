import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AISCA - Orientation Médecine", layout="wide")

st.title("AISCA 🩺 — Trouvez votre voie en Médecine")

st.markdown("""
Bienvenue jeune Padawan de 6ᵉ année ✨  
Renseigne tes compétences, tes expériences, tes vibes…  
Et AISCA t’aidera à révéler **ta spécialité idéale** 🌟
""")

st.subheader("📝 Formulaire")

skills = st.text_area("Décrivez vos compétences clés")
exp = st.text_area("Détaillez vos expériences professionnelles")
interests = st.text_area("Quelles sont vos appétences ?")

if st.button("Analyser mon profil 🧠"):
    user_payload = {
        "skills": skills,
        "experiences": exp,
        "interests": interests
    }

    try:
        response = requests.post("http://localhost:8000/analyze", json=user_payload)
        if response.status_code == 200:
            st.session_state["analysis"] = response.json()
            st.success("Analyse réussie ! Faites défiler pour voir vos résultats.")
        else:
            st.error("Erreur lors de l'analyse.")
    except:
        st.error("Impossible de contacter le backend 😭 Vérifie que FastAPI tourne.")

if "analysis" in st.session_state:
    result = st.session_state["analysis"]

    st.header("Résultats de l'analyse")

    st.subheader("Scores par blocs")
    st.json(result["block_scores"])

    st.subheader("Top métiers recommandés")
    st.json(result["jobs"])

if "analysis" in st.session_state:
    block_data = st.session_state["analysis"]["block_scores"]
    df = pd.DataFrame(block_data.items(), columns=["Bloc", "Score"])

    st.subheader("Radar / Bar Chart")
    
    fig, ax = plt.subplots()
    ax.bar(df["Bloc"], df["Score"])
    ax.set_ylabel("Score")
    ax.set_title("Scores par Bloc")
    st.pyplot(fig)
if "analysis" in st.session_state:
    job = st.session_state["analysis"]["jobs"][0]

    if st.button("Générer fiche métier IA"):
        payload = {
            "job_title": job["title"],
            "profile": skills + " " + exp + " " + interests
        }
        response = requests.post("http://localhost:8000/generate_fiche", json=payload)
        st.subheader("Fiche métier générée")
        st.write(response.json()["content"])
