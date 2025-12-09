# backend/models/sbert_model.py
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

# On charge le modèle UNE SEULE FOIS ici
model = SentenceTransformer(MODEL_NAME)

def embed_many(texts, normalize: bool = True):
    """
    texts: liste de strings
    return: np.array (n_texts, dim)
    """
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=normalize)

def embed_one(text: str, normalize: bool = True):
    """
    text: une seule chaîne
    return: vecteur 1D
    """
    return embed_many([text], normalize=normalize)[0]
