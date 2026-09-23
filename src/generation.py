import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.search import rechercher

load_dotenv()  # lit le fichier .env

# --- Bloc dépendant du fournisseur : c'est le seul à changer ---
client = genai.Client()  # utilise GEMINI_API_KEY
MODELE_LLM = "gemini-3.5-flash-lite"


def appeler_llm(consigne, message, tentatives=3):
    for essai in range(tentatives):
        try:
            reponse = client.models.generate_content(
                model=MODELE_LLM,
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=consigne,
                    temperature=0,
                ),
            )
            return reponse.text or "Je ne trouve pas cette information dans le guide."
        except Exception as e:
            if essai < tentatives - 1:
                print(f"  (erreur API, nouvelle tentative dans 5s : {e})")
                time.sleep(5)
            else:
                return f"[Erreur : le modèle n'a pas pu répondre après {tentatives} tentatives]"
# ---------------------------------------------------------------

CONSIGNE = """Tu es l'assistant du guide pratique de l'étudiant de l'Université de Tunis El Manar.
Tu réponds en français, uniquement à partir des extraits fournis.

Règles :
- N'utilise aucune connaissance extérieure aux extraits.
- Certains extraits peuvent être sans rapport avec la question : ignore-les.
- Si la réponse n'est pas dans les extraits, réponds exactement :
  "Je ne trouve pas cette information dans le guide."
- N'ajoute jamais de source quand tu réponds que l'information n'est pas dans le guide.
- Si un extrait contient un titre sans le contenu correspondant, dis que l'information n'est pas détaillée dans le guide.
- Termine par la source, au format : (Source : page X), uniquement quand tu donnes une vraie réponse.
- Sois concis : quelques phrases au maximum."""


def repondre(question, k=3):
    resultats = rechercher(question, k)
    contexte = "\n\n".join(
        f"[Extrait {i} - page {r['page']}]\n{r['texte']}"
        for i, r in enumerate(resultats, start=1)
    )
    message = f"Extraits du guide :\n\n{contexte}\n\nQuestion : {question}"
    return appeler_llm(CONSIGNE, message), resultats


if __name__ == "__main__":
    while True:
        question = input("\nQuestion (vide pour quitter) : ").strip()
        if not question:
            break
        texte, resultats = repondre(question)
        print("\n" + texte)
        print("\nChunks utilisés :", [(r["id"], r["page"]) for r in resultats])