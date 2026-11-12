"""Télécharge les 4 CSV (caracteristiques, lieux, usagers, vehicules) d'une année
depuis l'API data.gouv.fr (dataset BAAC 2005-2024) dans data/raw/<année>/.

Usage : python src/download_data.py --year 2023
"""
import argparse, re, sys
from pathlib import Path
import requests

DATASET = "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024"
API = f"https://www.data.gouv.fr/api/1/datasets/{DATASET}/"
# Les titres varient selon les années : caracteristiques-2020, carcteristiques-2022,
# caract-2023, Caract_2024. Le match exact écarte vehicules-immatricules-baac-<année>.
KINDS = {"caracteristiques": "carac?t(eristiques)?|carcteristiques", "lieux": "lieux",
         "usagers": "usagers", "vehicules": "vehicules"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2023)
    a = ap.parse_args()
    resp = requests.get(API, timeout=60)
    resp.raise_for_status()
    meta = resp.json()
    out = Path(__file__).resolve().parents[1] / "data" / "raw" / str(a.year)
    out.mkdir(parents=True, exist_ok=True)
    missing = []
    for kind, pattern in KINDS.items():
        title = re.compile(rf"({pattern})[-_]{a.year}\.csv", re.I)
        cands = [r for r in meta["resources"] if title.fullmatch(r.get("title") or "")]
        if not cands:
            print(f"[!] introuvable : {kind} {a.year}", file=sys.stderr)
            missing.append(kind); continue
        r = cands[0]
        dest = out / f"{kind}-{a.year}.csv"
        print("->", r["title"], r["url"])
        with requests.get(r["url"], stream=True, timeout=120) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(1 << 20):
                    f.write(chunk)
    if missing:
        sys.exit(f"Fichiers manquants : {', '.join(missing)}")
    print("OK ->", out)

if __name__ == "__main__":
    main()
