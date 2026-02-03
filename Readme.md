# PROJET IA GEN

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=for-the-badge&logo=google-gemini&logoColor=white)](https://aistudio.google.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

## 📌 Présentation du projet

Ce projet s’inscrit dans le cadre du **PROJET IA GEN** et vise à exploiter des techniques d’**IA générative et d’analyse sémantique** pour analyser, scorer et discriminer des compétences et métiers à partir de données textuelles.

L’application combine :
- une **API backend** (FastAPI) pour le traitement et le scoring,
- une **interface Streamlit** pour l’interaction utilisateur,
- l’API **Google Gemini** pour les traitements IA (embeddings, analyse sémantique, etc.).

L’objectif principal est d’aider à la **prise de décision** via des scores explicables (blocs de compétences, métiers, top résultats), en combinant questions ouvertes (analyse sémantique) et critères plus structurés.

---

## 🧱 Prérequis

*   Python **3.9+** recommandé
*   Gestionnaire de paquets `pip`
*   Une clé API **Google Gemini** valide

---

## ⚙️ Installation et configuration

### 1️⃣ Cloner le projet

```bash
git clone <url-du-repo>
cd PROJET-IA-GEN
```

### 2️⃣ Créer et activer un environnement virtuel

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configuration des variables d'environnement

À la racine du projet, créez un fichier `.env` :
```env
GEMINI_API_KEY=VOTRE_CLE_API_ICI
```

⚠️ Le fichier .env ne doit pas être versionné (présent dans le .gitignore).

### 5️⃣ Obtenir une clé API Gemini

1.  Rendez-vous sur [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Générez une nouvelle clé API.
3.  Copiez-la dans votre fichier `.env`.

---

## ▶️ Lancement du projet

### 🔹 Backend (FastAPI)

```bash
uvicorn backend.main:app --reload
```
*   **URL :** `http://127.0.0.1:8000`
*   **Swagger UI :** `http://127.0.0.1:8000/docs`

### 🔹 Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```
*   **URL :** `http://localhost:8501`

---

## 📂 Structure du projet
```text
PROJET-IA-GEN/
│
├── backend/            # API FastAPI
│   └── main.py
│
├── frontend/           # Interface Streamlit
│   └── app.py
│
├── requirements.txt    # Dépendances Python
├── .env                # Variables d’environnement (non versionné)
├── .gitignore
└── README.md
```

---

## 👥 Contributeurs

*   **Équipe Projet IA GEN** - *EFREI Paris*
*   Péma BELISE-PERREARD et Aurélien DIOGNE BOUGUENG