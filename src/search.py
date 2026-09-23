import json

import numpy as np
from sentence_transformers import SentenceTransformer

MODELE = "intfloat/multilingual-e5-small"

# Chargés une seule fois, au démarrage
with open("data/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)
embeddings = np.load("data/embeddings.npy")
model = SentenceTransformer(MODELE)


def rechercher(question, k=3):
    """Retourne les k chunks les plus proches de la question."""
    q = model.encode("query: " + question, normalize_embeddings=True)
    scores = embeddings @ q
    top = np.argsort(scores)[::-1][:k]
    return [
        {
            "id": chunks[i]["id"],
            "page": chunks[i]["page"],
            "texte": chunks[i]["texte"],
            "score": float(scores[i]),
        }
        for i in top
    ]


if __name__ == "__main__":
    while True:
        question = input("\nQuestion (vide pour quitter) : ").strip()
        if not question:
            break
        for r in rechercher(question):
            print(f"\n[chunk {r['id']} | page {r['page']}] score {r['score']:.3f}")
            print(r["texte"][:300] + "...")