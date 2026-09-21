from pypdf import PdfReader

PDF_PATH = "data/guide_etudiant_utm.pdf"
OUTPUT_PATH = "data/guide_etudiant_utm.txt"

reader = PdfReader(PDF_PATH)
print(f"Nombre de pages : {len(reader.pages)}")

pages = []
for numero, page in enumerate(reader.pages, start=1):
    texte = page.extract_text() or ""
    pages.append(texte)
    print(f"Page {numero} : {len(texte.split())} mots")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for numero, texte in enumerate(pages, start=1):
        f.write(f"\n\n=== PAGE {numero} ===\n{texte}")

print(f"Texte enregistré dans {OUTPUT_PATH}")