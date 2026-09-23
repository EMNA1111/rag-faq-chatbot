import streamlit as st

from src.generation import repondre

st.set_page_config(page_title="Assistant Guide Étudiant UTM", page_icon="🎓")

st.title("🎓 Assistant du guide de l'étudiant")
st.caption("Université de Tunis El Manar — pose une question sur le guide pratique")

if "historique" not in st.session_state:
    st.session_state.historique = []

question = st.chat_input("Pose ta question...")

if question:
    with st.spinner("Recherche en cours..."):
        reponse, chunks = repondre(question)
    st.session_state.historique.append((question, reponse, chunks))

for q, r, chunks in reversed(st.session_state.historique):
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.write(r)
        pages = sorted(set(c["page"] for c in chunks))
        with st.expander(f"Sources consultées (pages {', '.join(map(str, pages))})"):
            for c in chunks:
                st.markdown(f"**Chunk {c['id']} — page {c['page']}** (score {c['score']:.3f})")
                st.text(c["texte"][:300] + "...")