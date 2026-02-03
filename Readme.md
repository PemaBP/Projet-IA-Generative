# PROJET IA GEN

## 📌 Présentation du projet

Ce projet s’inscrit dans le cadre du **PROJET IA GEN** et vise à exploiter des techniques d’**IA générative et d’analyse sémantique** pour analyser, scorer et discriminer des compétences et métiers à partir de données textuelles.

L’application combine :
- une **API backend** (FastAPI) pour le traitement et le scoring,
- une **interface Streamlit** pour l’interaction utilisateur,
- l’API **Google Gemini** pour les traitements IA (embeddings, analyse sémantique, etc.).

L’objectif principal est d’aider à la **prise de décision** via des scores explicables (blocs de compétences, métiers, top résultats), en combinant questions ouvertes (analyse sémantique) et critères plus structurés.

---

## 🧱 Prérequis

- Python **3.9+** recommandé  
- `pip`
- Une clé API **Google Gemini**

---

## ⚙️ Installation et configuration

### 1️⃣ Cloner le projet

```bash
git clone <url-du-repo>
cd PROJET-IA-GEN

2️⃣ Créer et activer un environnement virtuel Python
Windows
python -m venv venv
venv\Scripts\activate

macOS / Linux
python3 -m venv venv
source venv/bin/activate


3️⃣ Installer les dépendances

Toutes les librairies nécessaires au projet sont listées dans le fichier requirements.txt.

pip install -r requirements.txt


4️⃣ Créer le fichier .env

À la racine du projet, créer un fichier .env et y renseigner la clé API Gemini :

GEMINI_API_KEY=VOTRE_CLE_API_ICI


⚠️ Le fichier .env ne doit pas être versionné (présent dans le .gitignore).


5️⃣ Créer une clé API Gemini

Se rendre sur Google AI Studio :
https://aistudio.google.com/app/apikey

Créer une nouvelle clé API

Copier la clé générée dans le fichier .env


▶️ Lancer le projet
🔹 Lancer l’API backend (FastAPI)

Depuis la racine du projet :
uvicorn backend.main:app --reload

    API accessible sur : http://127.0.0.1:8000

    Documentation Swagger : http://127.0.0.1:8000/docs

🔹 Lancer l’interface Streamlit

Dans un second terminal (environnement virtuel activé) :

streamlit run frontend/app.py
L’interface sera accessible à l’adresse indiquée dans le terminal (généralement http://localhost:8501
).

📂 Structure du projet
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