import json
import re
from pypdf import PdfReader

PDF_PATH = "data/guide_etudiant_utm.pdf"
OUTPUT_PATH = "data/chunks.json"

TAILLE_CHUNK = 200        # mots par chunk
CHEVAUCHEMENT = 40        # mots partagés entre deux chunks
PAGES_A_IGNORER = {1, 12}  # couverture + doublon de la page 9

PIED_DE_PAGE = re.compile(r"Guide pratique de l.étudiant de l.Université de Tunis El Manar")

CORRECTIONS = {
    "bilansobligatoires": "bilans obligatoires",
    "modérateursera": "modérateur sera",
    "publicannuelle": "public annuelle",
    "tunisienet": "tunisien et",
    "auxdifférentes": "aux différentes",
    "médecinegénéral": "médecine générale",
}


def recoller_lettres_espacees(ligne):
    """Répare les titres du type 'L ’ A C C È S  À  L ’ U N I V...'."""
    tokens = ligne.split()
    if len(tokens) >= 8 and sum(len(t) == 1 for t in tokens) / len(tokens) > 0.8:
        mots = re.split(r"\s{2,}", ligne.strip())
        return " ".join(m.replace(" ", "") for m in mots)
    return ligne


def nettoyer(texte, numero_page):
    texte = PIED_DE_PAGE.sub("", texte)
    numero_imprime = f"{numero_page - 1:02d}"   # ex. PDF page 7 -> imprimé "06"
    lignes = []
    for ligne in texte.splitlines():
        if ligne.strip() == numero_imprime:
            continue
        lignes.append(recoller_lettres_espacees(ligne))
    texte = " ".join(" ".join(lignes).split())
    for faux, juste in CORRECTIONS.items():
        texte = texte.replace(faux, juste)
    return texte


def decouper(mots, taille, chevauchement):
    if len(mots) <= taille * 1.3:
        return [mots]
    morceaux = []
    pas = taille - chevauchement
    debut = 0
    while True:
        morceaux.append(mots[debut:debut + taille])
        if debut + taille >= len(mots):
            break
        debut += pas
    return morceaux


reader = PdfReader(PDF_PATH)
chunks = []

for numero, page in enumerate(reader.pages, start=1):
    if numero in PAGES_A_IGNORER:
        continue
    texte = nettoyer(page.extract_text() or "", numero)
    for morceau in decouper(texte.split(), TAILLE_CHUNK, CHEVAUCHEMENT):
        chunks.append({
            "id": len(chunks) + 1,
            "page": numero,
            "texte": " ".join(morceau),
        })

for c in chunks:
    print(f"Chunk {c['id']:>2} | page {c['page']:>2} | {len(c['texte'].split())} mots")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"\n{len(chunks)} chunks enregistrés dans {OUTPUT_PATH}")