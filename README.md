# AAA – Projet ML : gravité des accidents corporels de la route (BAAC)

Projet du cours *Analyse de données et Apprentissage Automatique* (IMT Atlantique).
Données : [Bases de données annuelles des accidents corporels de la circulation routière 2005-2024](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/informations) (Licence Ouverte).

## Installation
```bash
make setup      # crée .venv et installe requirements.txt
make data       # télécharge l'année 2023 dans data/raw/2023/
make lab        # lance JupyterLab
```
## Structure
- `notebooks/` : notebooks (01 = exploration)
- `src/` : scripts utilitaires
- `data/raw/` (ignoré par git), `data/processed/` : données
- `reports/figures/` : figures exportées
