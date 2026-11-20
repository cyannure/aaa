"""Construit le jeu de données « une ligne = un accident » à partir des 4 CSV bruts
(data/raw/<année>/) et l'écrit dans data/processed/accidents_<année>.csv.

Cible `grav_max` : gravité de l'usager le plus touché de l'accident
(leger < hospitalise < tue ; il n'y a pas d'accident sans blessé dans les BAAC).

20 features, en 4 groupes :
- Accident (caracteristiques) : heure, week_end, lum, atm, agg, int, col
- Lieu (lieux, 1re ligne par accident) : catr, vma, surf, situ, nbv
- Conducteurs (usagers avec catu = 1, agrégés) : age_cond_max, part_cond_hommes,
  part_cond_loisirs, part_cond_proteges
- Véhicules (agrégés) : veh_vulnerable, choc_avant, manv_risquee, pieton_heurte

Usage : python src/build_dataset.py --year 2023
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Codes BAAC (2019+) du véhicule, regroupés du plus vulnérable au plus protégé
CATV_GROUPS = {
    "velo_edp": ["1", "50", "60", "80"],
    "2rm_3rm": ["2", "30", "31", "32", "33", "34", "35", "36", "41", "42", "43"],
    "vl_vu": ["3", "7", "10"],
    "lourd": ["13", "14", "15", "16", "17", "20", "21", "37", "38", "39", "40"],
}
GRAV_ORDER = {"1": 0, "4": 1, "3": 2, "2": 3}  # indemne < léger < hospitalisé < tué
GRAV_LABELS = {1: "leger", 2: "hospitalise", 3: "tue"}
MANV_RISQUEES = ["5", "6", "13", "14", "17", "18"]  # contresens, terre-plein, déporté, dépassement
CHOC_AVANT = ["1", "2", "3"]


def load(raw, kind, year):
    df = pd.read_csv(raw / f"{kind}-{year}.csv", sep=";", dtype=str, low_memory=False)
    # « -1 » (souvent « -1 » avec espace) = non renseigné
    return df.apply(lambda s: s.str.strip()).replace({"-1": np.nan, "": np.nan})


def build(year):
    raw = ROOT / "data" / "raw" / str(year)
    car, lieux, usa, veh = (load(raw, k, year) for k in
                            ["caracteristiques", "lieux", "usagers", "vehicules"])

    # Cible : gravité maximale sur tous les usagers (conducteurs, passagers, piétons)
    rank = usa["grav"].map(GRAV_ORDER)
    y = rank.groupby(usa["Num_Acc"]).max().map(GRAV_LABELS).rename("grav_max")

    # Accident
    acc = car.set_index("Num_Acc")
    date = pd.to_datetime(acc["an"] + "-" + acc["mois"] + "-" + acc["jour"], format="%Y-%m-%d")
    X = pd.DataFrame({
        "heure": acc["hrmn"].str[:2].astype(float),
        "week_end": (date.dt.dayofweek >= 5).astype(int),
    }, index=acc.index)
    X = X.join(acc[["lum", "atm", "agg", "int", "col"]])

    # Lieu : un accident peut avoir plusieurs lignes (plusieurs voies) ; on garde la 1re
    lieu = lieux.drop_duplicates("Num_Acc").set_index("Num_Acc")
    X = X.join(lieu[["catr", "surf", "situ"]])
    X["vma"] = pd.to_numeric(lieu["vma"])
    # « #VALEURMULTI » -> NaN ; 0 voie = non renseigné selon la documentation BAAC
    X["nbv"] = pd.to_numeric(lieu["nbv"], errors="coerce").replace(0, np.nan)

    # Conducteurs (catu = 1)
    cond = usa[usa["catu"] == "1"].copy()
    cond["age"] = year - pd.to_numeric(cond["an_nais"])
    cond["homme"] = cond["sexe"].map({"1": 1.0, "2": 0.0})
    cond["loisirs"] = cond["trajet"].replace("0", np.nan).map(lambda t: t if pd.isna(t) else float(t == "5"))
    secu = cond[["secu1", "secu2", "secu3"]]
    # Protégé = ceinture (1) ou casque (2) ; non déterminable (8) ou absent -> NaN
    cond["protege"] = np.where(secu.isin(["1", "2"]).any(axis=1), 1.0,
                               np.where(cond["secu1"].isna() | (cond["secu1"] == "8"), np.nan, 0.0))
    g = cond.groupby("Num_Acc")
    X["age_cond_max"] = g["age"].max()
    X["part_cond_hommes"] = g["homme"].mean()
    X["part_cond_loisirs"] = g["loisirs"].mean()
    X["part_cond_proteges"] = g["protege"].mean()

    # Véhicules
    grp = {code: i for i, codes in enumerate(CATV_GROUPS.values()) for code in codes}
    veh["catv_rank"] = veh["catv"].map(grp)  # 0 = plus vulnérable ; indéterminé/autre -> NaN
    g = veh.groupby("Num_Acc")
    X["veh_vulnerable"] = g["catv_rank"].min().map(dict(enumerate(CATV_GROUPS)))
    X["choc_avant"] = g["choc"].agg(lambda s: int(s.isin(CHOC_AVANT).any()))
    X["manv_risquee"] = g["manv"].agg(lambda s: int(s.isin(MANV_RISQUEES).any()))
    X["pieton_heurte"] = g["obsm"].agg(lambda s: int((s == "1").any()))

    df = X.join(y, how="inner")
    return df.reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2023)
    a = ap.parse_args()
    df = build(a.year)
    out = ROOT / "data" / "processed" / f"accidents_{a.year}.csv"
    df.to_csv(out, index=False)
    print(df.shape, "->", out)
    print(df["grav_max"].value_counts(normalize=True).round(3).to_string())


if __name__ == "__main__":
    main()
