# CLAUDE.md – Projet ML « gravité des accidents corporels de la route »

## Contexte
Projet noté du cours *Analyse de données et Apprentissage Automatique* (IMT Atlantique, 2026-2027, intervenant Bilal Said).
Équipe de 2 étudiants. Tâche : **classification** sur le dataset BAAC (Bases de données annuelles des accidents corporels de la circulation routière, 2005-2024, data.gouv.fr, Licence Ouverte).
Source : https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/informations
Repo : https://github.com/cyannure/aaa
Les diapos de cours et le sujet (`AAA - Project.pdf`) sont dans le dossier parent (`../`).

## Données
- 4 CSV par année, séparateur `;` : `caracteristiques`, `lieux`, `usagers`, `vehicules`.
- Clé : `Num_Acc` (accident) ; `id_vehicule` / `num_veh` relient usagers et véhicules.
- **Décision : une instance = un accident** (54 822 en 2023). Cible `grav_max` = gravité de l'usager le plus touché : `leger` 63,9 %, `hospitalise` 30,2 %, `tue` 5,8 % (pas d'accident sans blessé). 3 classes ou binaire (grave = hospitalise+tue) : **à décider en équipe**.
- `make dataset` (`src/build_dataset.py`) → `data/processed/accidents_<année>.csv`, 20 features en 4 groupes : accident (`heure`, `week_end`, `lum`, `atm`, `agg`, `int`, `col`), lieu (1re ligne `lieux` par accident : `catr`, `vma`, `surf`, `situ`, `nbv`), conducteurs agrégés (`age_cond_max`, `part_cond_hommes`, `part_cond_loisirs`, `part_cond_proteges`), véhicules agrégés (`veh_vulnerable`, `choc_avant`, `manv_risquee`, `pieton_heurte`). Les codes BAAC (`lum`… `situ`, `veh_vulnerable`) sont catégoriels même s'ils sont lus comme nombres.
- Une ligne par accident : pas besoin de split groupé.
- **Test set** : 20 % stratifié sur `grav_max` (`train_test_split`, `random_state=42`) mis de côté dès le chargement ; toute l'EDA et tous les `fit` se font sur `train`.
- **Valeurs manquantes** (décidé) : `vma` = médiane selon `agg` (80 hors agglo, 50 en agglo) via `ImputeurParGroupe` + `vma_manquant` ; autres numériques = médiane + indicateur (`add_indicator=True`), car l'absence est liée à la gravité ; catégorielles = valeur la plus fréquente sans indicateur (< 0,5 % de manquants). `nbv = 0` = non renseigné (NaN).
- **Corrélations (EDA section 5)** : `vma`/`agg`/`catr` redondantes (0,62-0,77) mais les plus liées à la cible ; `pieton_heurte`, `choc_avant`, `heure` (effet cyclique), `surf` faibles. Décisions *proposées*, à valider en équipe : comparer jeu A (20 variables) vs jeu B (sans `pieton_heurte` ni `choc_avant`) ; `heure` en sin/cos ; `vma` en catégories pour les modèles linéaires (effet non monotone : 80 km/h plus grave que 130).
- Dans les BAAC, `-1` = non renseigné (à traiter comme NaN).
- Année de travail par défaut : 2023 (~125 000 usagers). Le dataset complet est trop gros pour les consignes ; **pas de séries temporelles**.
- Téléchargement : `make data` (`src/download_data.py --year 2023`) → `data/raw/<année>/` (ignoré par git). Le livrable final doit charger une version allégée hébergée sur GitHub (`data/processed/`).
- Les titres des ressources data.gouv varient selon les années (`caract-2023.csv`, `carcteristiques-2022.csv`, `Caract_2024.csv`) : `download_data.py` les reconnaît par motif exact (testé pour 2005-2025).

## Consignes du sujet (à respecter strictement)
**Périmètre** : 10-20 features, quelques 10k-100k instances, numériques ET catégorielles, données réelles. Exclure : données simulées, séries temporelles, flux, systèmes de recommandation, génération/résumé. Régression/classification + tuning d'hyperparamètres.

**Livrable** : un seul notebook Google Colab, régulièrement poussé sur GitHub public, bien documenté, organisé en sections, chargement des données et installation des libs minimaux.

**Structure du notebook** :
1. Description projet/dataset (objectifs, solutions existantes, URL sources).
2. Cellule unique de tous les imports (commentaires sur versions/installation).
3. Accès aux données (URL GitHub + code de chargement ; sinon Google Drive).
4. Analyse exploratoire : métadonnées (nb instances/features/types), valeurs manquantes (identification, stratégies possibles et choisie, argumentées), distributions/scaling/outliers, étude de la cible (déséquilibre + décision), corrélations/sélection/réduction de dimension/anomalies, clustering non supervisé (lien avec la cible), interprétations et conclusions.
5. Baselines et ensembles : splits train/val/test, pipelines, entraînement/validation, test, discussion.
6. Modèles améliorés, tuning, analyse (justification des choix).

**Obligations** :
- Feature engineering de nouvelles variables.
- **Nested CV**, même nombre de folds pour tous les modèles.
- **Learning curves**.
- Mêmes métriques pour tous les modèles, comparés sur les mêmes graphiques.
- Évaluation sur un **test set jamais vu** ; comparer tous les modèles (sur-apprentissage vs généralisation).
- **Down/up-sampling uniquement sur le train**, après le split.
- **Pas de modèle linéaire/polynomial non régularisé. Pas d'arbre de décision seul.** Versions polynomiales de modèles linéaires recommandées.
- Si une partie du train est utilisée au début, le train complet doit l'être ensuite.
- **Ensembles avancés** obligatoires (boosting, stacking…).
- **Tuning** de plusieurs hyperparamètres significatifs avec plages de valeurs, et **graphiques en coordonnées parallèles**.
- Documenter ce qui a marché ET ce qui n'a pas marché (dans un notebook séparé).
- Recommandé : faire critiquer le projet par un LLM (hypothèses, erreurs, améliorations). Bonus pour le prétraitement/enrichissement multi-sources/feature engineering.

## Planning
- 16 oct : équipes et sujets (fait)
- 23 oct : analyse exploratoire + non supervisé (**dépassé**, à rattraper)
- **20 nov : baselines et ensembles**
- 27 nov : modèles améliorés, tuning, analyse
- 4 déc : rendu final ; 11 déc : soutenance

Notation (indicatif) : 5 % consignes, 5 % organisation, 30 % exploration + non supervisé, 30 % baselines/ensembles, 30 % modèles améliorés/tuning.

## Structure du repo
- `notebooks/` : `01_exploration.ipynb` (squelette : chargement, fusion, NaN, cible, distributions)
- `src/download_data.py` : téléchargement des CSV
- `data/raw/` (git-ignoré), `data/processed/`, `reports/figures/`
- `Makefile` : `make setup`, `make data`, `make lab` ; `requirements.txt`

## Conventions de travail
- Python 3, venv `.venv` ; `random_state=42` partout pour la reproductibilité.
- Notebooks commentés en français ; code en anglais ou français de façon cohérente.
- Éviter les fuites de données : tout fit (imputation, scaling, encodage, rééchantillonnage) dans un `Pipeline` / sur le train seul.
- Le livrable final doit tourner sur Colab depuis un notebook unique : garder les chemins relatifs et prévoir le chargement depuis l'URL GitHub brute.
- Deux personnes sur le repo : `git pull` avant de travailler, se répartir les sections pour éviter les conflits sur les `.ipynb`.
- Ne pas committer les gros CSV bruts.

## Prochaines étapes
1. Décider : cible 3 classes ou binaire.
2. Pousser `data/processed/accidents_2023.csv` sur GitHub (le notebook le charge depuis l'URL brute si le fichier local manque).
3. Compléter l'EDA : corrélations (Cramér's V), PCA/UMAP, K-Means vs `grav`, choix de prétraitement.
4. Feature engineering, puis baselines et ensembles (nested CV, learning curves) pour le 20 nov.
