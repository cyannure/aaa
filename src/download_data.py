"""Télécharge les 4 CSV (caracteristiques, lieux, usagers, vehicules) d'une année
depuis l'API data.gouv.fr (dataset BAAC 2005-2024) dans data/raw/<année>/.

Usage : python src/download_data.py --year 2023
"""
import argparse, re, sys
from pathlib import Path
import requests

DATASET = "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024"
API = f"https://www.data.gouv.fr/api/1/datasets/{DATASET}/"
KINDS = ["caracteristiques", "lieux", "usagers", "vehicules"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2023)
    a = ap.parse_args()
    meta = requests.get(API, timeout=60).json()
    out = Path(__file__).resolve().parents[1] / "data" / "raw" / str(a.year)
    out.mkdir(parents=True, exist_ok=True)
    for kind in KINDS:
        cands = [r for r in meta["resources"]
                 if r.get("format", "").lower() == "csv"
                 and kind in r["title"].lower() and str(a.year) in r["title"]]
        if not cands:
            print(f"[!] introuvable : {kind} {a.year}", file=sys.stderr); continue
        r = cands[0]
        dest = out / f"{kind}-{a.year}.csv"
        print("->", r["title"], r["url"])
        with requests.get(r["url"], stream=True, timeout=120) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(1 << 20):
                    f.write(chunk)
    print("OK ->", out)

if __name__ == "__main__":
    main()
