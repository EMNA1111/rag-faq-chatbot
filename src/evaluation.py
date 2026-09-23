import csv

from generation import repondre

with open("data/tests.csv", encoding="utf-8") as f:
    tests = list(csv.DictReader(f))

resultats = []
for t in tests:
    reponse, chunks_trouves = repondre(t["question"])
    pages_trouvees = [c["page"] for c in chunks_trouves]

    if t["type"] == "dans_document":
        # succès si la page attendue est dans les chunks utilisés
        ok = int(t["page_pdf"]) in pages_trouvees
    else:
        # hors_document : succès si le bot dit ne pas trouver l'information
        ok = "ne trouve pas" in reponse.lower()

    resultats.append({"question": t["question"], "type": t["type"], "ok": ok, "reponse": reponse})
    statut = "OK  " if ok else "RATE"
    print(f"{statut} [{t['type']:14}] {t['question'][:60]}")

reussies = sum(r["ok"] for r in resultats)
print(f"\n{reussies}/{len(resultats)} tests réussis")

print("\nDétail des échecs :")
for r in resultats:
    if not r["ok"]:
        print(f"\n- {r['question']}")
        print(f"  Réponse du bot : {r['reponse'][:200]}")