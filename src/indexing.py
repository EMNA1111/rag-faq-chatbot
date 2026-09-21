import csv
import json

import numpy as np
from sentence_transformers import SentenceTransformer

MODELE = "intfloat/multilingual-e5-small"
K = 3  # nombre de chunks retournés par question

# 1. Charger les chunks
with open("data/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

# 2. Transformer chaque chunk en vecteur
# (le modèle e5 exige le préfixe "passage: " pour les documents)
model = SentenceTransformer(MODELE)
textes = ["passage: " + c["texte"] for c in chunks]
embeddings = model.encode(textes, normalize_embeddings=True, show_progress_bar=True)
np.save("data/embeddings.npy", embeddings)
print(f"\n{len(chunks)} chunks -> matrice {embeddings.shape}, enregistrée dans data/embeddings.npy")

# 3. Test rapide : la bonne page est-elle dans les K meilleurs chunks ?
with open("data/tests.csv", encoding="utf-8") as f:
    tests = [r for r in csv.DictReader(f) if r["type"] == "dans_document"]

trouves = 0
for t in tests:
    # préfixe "query: " pour les questions
    q = model.encode("query: " + t["question"], normalize_embeddings=True)
    scores = embeddings @ q  # vecteurs normalisés : produit scalaire = similarité cosinus
    top = np.argsort(scores)[::-1][:K]
    pages = [chunks[i]["page"] for i in top]
    ok = int(t["page_pdf"]) in pages
    trouves += ok
    print(f"{'OK   ' if ok else 'RATE '} {t['question'][:55]:55} -> pages {pages} (attendu {t['page_pdf']})")

print(f"\n{trouves}/{len(tests)} questions avec la bonne page dans le top {K}")