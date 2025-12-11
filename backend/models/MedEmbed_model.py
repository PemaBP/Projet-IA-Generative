from sentence_transformers import SentenceTransformer
import numpy as np
 
class MedEmbed:
    def __init__(self, model_name="abhinand/MedEmbed-base-v0.1"):
        self.model = SentenceTransformer(model_name)
 
    def embed(self, text: str, normalize=True):
        emb = self.model.encode(text, convert_to_numpy=True)
        if normalize:
            emb = emb / (np.linalg.norm(emb) + 1e-9)
        return emb
 
    def embed_many(self, texts, normalize=True):
        embs = self.model.encode(texts, convert_to_numpy=True)
        if normalize:
            norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-9
            embs = embs / norms
        return embs
 
# Instance globale du modèle (évite rechargement)
sbert = MedEmbed()
 
def embed(text, normalize=True):
    return sbert.embed(text, normalize)
 
def embed_many(texts, normalize=True):
    return sbert.embed_many(texts, normalize)