import csv
from pathlib import Path

import streamlit as st

from src.generation import repondre

BLEU = "#2F39A9"
BLEU_FONCE = "#232C86"

st.set_page_config(page_title="Assistant Guide Étudiant UTM", page_icon="🎓")

st.markdown(
    f"""
<style>
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
.block-container {{ max-width: 860px; padding-top: 1.2rem; padding-bottom: 6rem; }}

.bandeau {{
    background: linear-gradient(135deg, {BLEU_FONCE}, {BLEU});
    color: #fff; border-radius: 16px; padding: 16px 22px;
    display: flex; align-items: center; gap: 14px;
}}
.bandeau .logo {{
    background: rgba(255,255,255,.14); border-radius: 12px;
    width: 42px; height: 42px; display: flex; align-items: center;
    justify-content: center; font-size: 22px;
}}
.bandeau .titre {{ font-weight: 700; font-size: 1.1rem; line-height: 1.2; }}
.bandeau .sous-titre {{ font-size: .82rem; opacity: .85; }}

.accueil {{ text-align: center; margin: 2.2rem 0 1.4rem; }}
.accueil .logo {{
    background: {BLEU}; width: 64px; height: 64px; border-radius: 18px;
    display: inline-flex; align-items: center; justify-content: center; font-size: 32px;
}}
.accueil h2 {{ color: {BLEU}; margin: 14px 0 4px; font-size: 1.6rem; }}
.accueil p {{ color: #6B7280; margin: 0; }}

div[data-testid="stButton"], div[data-testid="stButton"] > button {{ width: 100%; }}
div[data-testid="stButton"] > button {{
    background: #fff; color: #1F2547; border: 1px solid #DDE0F3;
    border-radius: 14px; min-height: 72px; height: auto; padding: 12px 16px;
    justify-content: flex-start; text-align: left;
    box-shadow: 0 1px 3px rgba(47,57,169,.08);
}}
div[data-testid="stButton"] > button p {{ text-align: left; }}
div[data-testid="stButton"] > button:hover {{ border-color: {BLEU}; color: {BLEU}; }}

.note {{ text-align: center; color: #8A90A6; font-size: .78rem; margin-top: 1rem; }}
</style>
""",
    unsafe_allow_html=True,
)

# --- Suggestions : uniquement des questions présentes dans la base de tests ---
EMOJIS = {
    "restaurant": "🍽️", "médecine": "⚕️", "baccalauréat": "🎓",
    "séjour": "🪪", "renouvellement": "🔄", "solvabilité": "📄",
}
PAR_DEFAUT = [
    "Quel est le prix maximum d'un repas au restaurant universitaire ?",
    "Quelle mention au baccalauréat faut-il pour entrer en médecine ?",
]


def charger_suggestions(n=6):
    chemin = Path(__file__).parent / "data" / "tests.csv"
    try:
        with open(chemin, encoding="utf-8") as f:
            questions = [
                r["question"].strip()
                for r in csv.DictReader(f)
                if r.get("type") == "dans_document"
            ]
    except OSError:
        questions = []
    return (questions or PAR_DEFAUT)[:n]


def emoji_pour(question):
    q = question.lower()
    return next((e for mot, e in EMOJIS.items() if mot in q), "💬")


def afficher_sources(chunks):
    pages = sorted({c["page"] for c in chunks})
    with st.expander(f"Sources consultées (pages {', '.join(map(str, pages))})"):
        for c in chunks:
            st.markdown(f"**Chunk {c['id']} — page {c['page']}** (score {c['score']:.3f})")
            st.text(c["texte"][:300] + "...")


def choisir(question):
    st.session_state.pending = question


# --- État et saisie ---
if "historique" not in st.session_state:
    st.session_state.historique = []

st.markdown(
    """
<div class="bandeau">
  <div class="logo">🎓</div>
  <div>
    <div class="titre">Assistant du guide de l'étudiant</div>
    <div class="sous-titre">Université de Tunis El Manar — pose une question sur le guide pratique</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

pending = st.session_state.pop("pending", None)
question = st.chat_input("Pose ta question...") or pending

# --- Écran d'accueil (tant qu'aucune question n'a été posée) ---
if not st.session_state.historique and not question:
    st.markdown(
        """
<div class="accueil">
  <div class="logo">🎓</div>
  <h2>Bonjour, je suis ton assistant !</h2>
  <p>Pose-moi une question sur le guide pratique de l'étudiant de l'UTM.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    suggestions = charger_suggestions()
    for i in range(0, len(suggestions), 2):
        colonnes = st.columns(2)
        for col, q in zip(colonnes, suggestions[i:i + 2]):
            col.button(f"{emoji_pour(q)}  {q}", key=f"sugg_{i}_{q[:20]}", on_click=choisir, args=(q,))

# --- Conversation (la plus ancienne en haut) ---
for q, r, chunks in st.session_state.historique:
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.write(r)
        afficher_sources(chunks)

if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            reponse, chunks = repondre(question)
        st.write(reponse)
        afficher_sources(chunks)
    st.session_state.historique.append((question, reponse, chunks))

st.markdown(
    '<div class="note">Les réponses sont basées uniquement sur le guide officiel UTM. '
    "En cas de doute, consulte ton administration.</div>",
    unsafe_allow_html=True,
)