# rag-faq-chatbot
# Assistant du guide de l'étudiant (UTM)

Chatbot de type RAG (Retrieval-Augmented Generation) qui répond aux questions des étudiants de l'Université de Tunis El Manar à partir du guide pratique de l'étudiant (PDF). Chaque réponse cite la page du guide dont elle provient. Si l'information n'est pas dans le guide, l'assistant le dit au lieu d'inventer.

## Fonctionnement

```
PDF  ->  texte nettoyé  ->  chunks  ->  embeddings  ->  recherche des 3 meilleurs chunks  ->  réponse Gemini + source
```

1. **Extraction** : le texte du PDF est extrait et nettoyé.
2. **Découpage** : le texte est découpé en chunks d'environ 200 mots, chacun associé à sa page.
3. **Indexation** : chaque chunk est transformé en vecteur avec `intfloat/multilingual-e5-small` (préfixes `passage:` et `query:`).
4. **Recherche** : la question est encodée, puis les 3 chunks les plus proches (similarité cosinus) sont retenus.
5. **Génération** : un modèle Gemini répond uniquement à partir de ces extraits et indique la page source.

## Structure du projet

```
rag-faq-chatbot/
├── app.py                  # interface Streamlit
├── src/
│   ├── extract_text.py     # PDF -> texte
│   ├── chunking.py         # texte -> chunks.json
│   ├── indexing.py         # chunks -> embeddings.npy + test de recherche
│   ├── search.py           # recherche des chunks les plus proches
│   ├── generation.py       # prompt + appel à Gemini
│   └── evaluation.py       # évaluation sur data/tests.csv
├── data/
│   ├── guide_etudiant_utm.pdf
│   └── tests.csv           # questions de test
├── .streamlit/config.toml  # thème de l'interface
├── requirements.txt
└── .env                    # clé API (non versionné)
```

## Installation

Prérequis : Python 3.10 ou plus récent et une clé API Gemini (Google AI Studio).

```bash
git clone <url-du-depot>
cd rag-faq-chatbot
python -m venv venv
venv\Scripts\activate          # Windows (PowerShell / cmd)
pip install -r requirements.txt
```

Créez un fichier `.env` à la racine :

```
GEMINI_API_KEY=votre_cle_ici
```

## Utilisation

Les fichiers `data/guide_etudiant_utm.txt`, `data/chunks.json` et `data/embeddings.npy` sont générés et non versionnés. Il faut donc exécuter les scripts **dans cet ordre**, depuis la racine du projet :

```bash
python src/extract_text.py     # 1. PDF -> texte
python src/chunking.py         # 2. texte -> chunks
python src/indexing.py         # 3. chunks -> embeddings (télécharge le modèle, ~470 Mo la première fois)
streamlit run app.py           # 4. lance l'interface sur http://localhost:8501
```

Le premier chargement de l'interface est lent (chargement de PyTorch et du modèle d'embeddings). Les questions suivantes sont beaucoup plus rapides.

## Évaluation

Le jeu de test `data/tests.csv` contient 15 questions : des questions dont la réponse est dans le guide, et des questions dont la réponse n'y est pas (l'assistant doit alors refuser de répondre).

```bash
python src/evaluation.py
```

| Mesure | Résultat |
|---|---|
| Score global | **À COMPLÉTER** / 15 |
| Bonne page dans le top 3 (`indexing.py`) | **À COMPLÉTER** / **À COMPLÉTER** |

## Limites

- L'assistant ne connaît que le contenu du guide : il ne répond pas aux questions hors sujet.
- Une information coupée entre deux chunks peut être mal retrouvée.
- Le temps de réponse dépend de l'API Gemini. Le palier gratuit est limité en quota et peut renvoyer des erreurs 503 aux heures de forte demande (le code réessaie automatiquement).
- Le guide date de sa publication : les prix, dates et procédures peuvent avoir changé. En cas de doute, il faut consulter l'administration.

## Technologies

Python, Streamlit, sentence-transformers (`intfloat/multilingual-e5-small`), NumPy, Google Gemini (`google-genai`).