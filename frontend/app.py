import streamlit as st
import requests

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
