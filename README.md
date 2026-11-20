# AAA – Projet ML : gravité des accidents corporels de la route (BAAC)

Projet du cours *Analyse de données et Apprentissage Automatique* (IMT Atlantique).
Données : [Bases de données annuelles des accidents corporels de la circulation routière 2005-2024](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/informations) (Licence Ouverte).

## Installation
```bash
make setup      # crée .venv et installe requirements.txt
make data       # télécharge l'année 2023 dans data/raw/2023/
make dataset    # construit data/processed/accidents_2023.csv (1 ligne = 1 accident)
make lab        # lance JupyterLab
```
## Jeu de données (`data/processed/accidents_2023.csv`)
Une ligne = un accident corporel de 2023 (54 822 accidents), construite par `src/build_dataset.py` à partir des 4 tables BAAC.
Libellés des codes : [description officielle des bases BAAC](https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2025/20261030-133723/description-des-bases-de-donnees-annuelles.pdf).
Une case vide signifie « non renseigné » (codé `-1` dans les fichiers bruts).

### Cible
| Variable | Description | Valeurs |
|---|---|---|
| `grav_max` | Gravité de l'usager le plus touché de l'accident (conducteurs, passagers et piétons). | `leger` (soins sans hospitalisation > 24 h), `hospitalise` (> 24 h), `tue` (décès dans les 30 jours) |

### Accident (table `caracteristiques`)
| Variable | Description | Valeurs |
|---|---|---|
| `heure` | Heure de l'accident, tirée de `hrmn`. | 0 à 23 |
| `week_end` | Accident un samedi ou un dimanche. | 0 = non, 1 = oui |
| `lum` | Conditions d'éclairage. | 1 plein jour ; 2 crépuscule ou aube ; 3 nuit sans éclairage public ; 4 nuit avec éclairage public non allumé ; 5 nuit avec éclairage public allumé |
| `atm` | Conditions atmosphériques. | 1 normale ; 2 pluie légère ; 3 pluie forte ; 4 neige, grêle ; 5 brouillard, fumée ; 6 vent fort, tempête ; 7 temps éblouissant ; 8 temps couvert ; 9 autre |
| `agg` | Localisation par rapport à une agglomération. | 1 hors agglomération ; 2 en agglomération |
| `int` | Type d'intersection. | 1 hors intersection ; 2 en X ; 3 en T ; 4 en Y ; 5 à plus de 4 branches ; 6 giratoire ; 7 place ; 8 passage à niveau ; 9 autre |
| `col` | Type de collision. | 1 deux véhicules, frontale ; 2 deux véhicules, par l'arrière ; 3 deux véhicules, par le côté ; 4 trois véhicules et plus, en chaîne ; 5 trois véhicules et plus, collisions multiples ; 6 autre collision ; 7 sans collision |

### Lieu (table `lieux`, première ligne de l'accident)
| Variable | Description | Valeurs |
|---|---|---|
| `catr` | Catégorie de route. | 1 autoroute ; 2 route nationale ; 3 route départementale ; 4 voie communale ; 5 hors réseau public ; 6 parc de stationnement ouvert à la circulation ; 7 route de métropole urbaine ; 9 autre |
| `vma` | Vitesse maximale autorisée sur le lieu de l'accident. | 10 à 130 km/h |
| `surf` | État de la surface de la chaussée. | 1 normale ; 2 mouillée ; 3 flaques ; 4 inondée ; 5 enneigée ; 6 boue ; 7 verglacée ; 8 corps gras, huile ; 9 autre |
| `situ` | Situation de l'accident sur la voie. | 0 aucune ; 1 sur chaussée ; 2 sur bande d'arrêt d'urgence ; 3 sur accotement ; 4 sur trottoir ; 5 sur piste cyclable ; 6 sur autre voie spéciale ; 8 autre |
| `nbv` | Nombre total de voies de circulation. | 1 à 12 (0 veut dire « non renseigné » dans les BAAC : converti en case vide) |

### Conducteurs (table `usagers`, `catu = 1`, agrégés sur l'accident)
| Variable | Description | Valeurs |
|---|---|---|
| `age_cond_max` | Âge du conducteur le plus âgé (2023 − année de naissance). | 4 à 100 ans |
| `part_cond_hommes` | Part d'hommes parmi les conducteurs. | 0 à 1 |
| `part_cond_loisirs` | Part des conducteurs dont le trajet est « promenade, loisirs » (motif non renseigné exclu). | 0 à 1 |
| `part_cond_proteges` | Part des conducteurs portant une ceinture ou un casque (« non déterminable » exclu). | 0 à 1 |

### Véhicules (table `vehicules`, agrégés sur l'accident)
| Variable | Description | Valeurs |
|---|---|---|
| `veh_vulnerable` | Catégorie du véhicule le plus vulnérable impliqué, en regroupant les codes `catv`. | `velo_edp` (vélo, trottinette, vélo électrique) ; `2rm_3rm` (cyclomoteur, scooter, moto, 3 roues, quad) ; `vl_vu` (voiture, voiturette, utilitaire) ; `lourd` (poids lourd, tracteur, engin spécial, bus, car, train, tramway) |
| `choc_avant` | Au moins un véhicule a un point de choc initial à l'avant (avant, avant droit ou avant gauche). | 0 = non, 1 = oui |
| `manv_risquee` | Au moins un véhicule circulait à contresens, franchissait le terre-plein central, s'est déporté ou dépassait. | 0 = non, 1 = oui |
| `pieton_heurte` | Au moins un véhicule a heurté un piéton (obstacle mobile `obsm = 1`). | 0 = non, 1 = oui |

## Préparation des données : étapes et justifications
Du téléchargement des fichiers bruts au jeu prêt pour les modèles, dans l'ordre. Les étapes 1 à 5 sont dans `src/download_data.py` et `src/build_dataset.py`, l'étape 6 dans `notebooks/01_exploration.ipynb`.

### 1. Téléchargement (`make data`)
- **Choix des fichiers par leur nom exact.** Les noms changent selon les années (`caracteristiques-2020.csv`, `carcteristiques-2022.csv`, `caract-2023.csv`, `Caract_2024.csv`). Un autre fichier, `vehicules-immatricules-baac-2023.csv`, contient lui aussi « vehicules » et l'année : une recherche par mot-clé l'aurait téléchargé à la place de `vehicules-2023.csv`.
- **Une seule année, 2023.** Plusieurs années formeraient une série temporelle, exclue par le sujet ; une année suffit à atteindre quelques dizaines de milliers d'instances.

### 2. Nettoyage des valeurs brutes
- **Espaces supprimés** autour de toutes les valeurs : la base contient par exemple `" -1"` au lieu de `"-1"`.
- **`-1` et cases vides convertis en valeurs manquantes.** Dans les BAAC, `-1` signifie « non renseigné ».
- **D'autres codes signifient aussi « non renseigné »** et sont convertis en manquants, conformément à la documentation BAAC :
  - `nbv = 0` (0 voie) et `nbv = #VALEURMULTI` ;
  - `trajet = 0` ;
  - `secu1 = 8` (« non déterminable ») ;
  - `catv = 0` (« indéterminable ») et `catv = 99` (« autre véhicule »), qui ne peuvent être classés dans aucun groupe.

### 3. Choix de l'unité : une ligne = un accident
- **Le problème :** la table `usagers` compte 125 789 lignes en 2023, au-delà des 100 000 instances maximum du sujet. Une fusion naïve sur `Num_Acc` dupliquait en plus 37 894 usagers, car 15 870 accidents ont plusieurs lignes dans `lieux`.
- **La décision :** une ligne par accident, soit 54 822 instances. Il faut alors résumer en une valeur les conducteurs et véhicules de chaque accident (étapes 4 et 5).
- **La conséquence :** un même accident ne peut pas se retrouver à la fois dans le train et dans le test, donc un découpage stratifié classique suffit.

### 4. Construction de la cible `grav_max`
- **Gravité de l'usager le plus touché** de l'accident, en comptant conducteurs, passagers et piétons. Ordre utilisé : indemne < blessé léger < hospitalisé < tué. Les usagers dont la gravité est inconnue sont ignorés.
- **Codes BAAC remplacés par des libellés :** dans la base, l'ordre des codes (1 indemne, 2 tué, 3 hospitalisé, 4 léger) ne suit pas la gravité ; les libellés `leger`, `hospitalise` et `tue` évitent toute confusion.
- **Pas de classe « indemne » :** la base ne recense que les accidents corporels, qui ont tous au moins un blessé. La cible a donc 3 classes : léger 63,9 %, hospitalisé 30,2 %, tué 5,8 %.

### 5. Construction et regroupement des variables (55 colonnes → 20)
**Accident** (table `caracteristiques`, une ligne par accident, rien à résumer) :
- **`heure` :** les deux premiers chiffres de `hrmn` (`"17:45"` → 17). Les minutes n'apportent rien à cette échelle.
- **`week_end` :** calculée à partir de `jour`, `mois` et `an` (samedi ou dimanche = 1). Elle résume la date en un comportement (trafic de loisirs) sans en faire une série temporelle.
- **`lum`, `atm`, `agg`, `int`, `col` :** reprises telles quelles. Ce sont des codes, donc des variables catégorielles même s'ils s'écrivent avec des chiffres.

**Lieu** (table `lieux`) :
- **Première ligne de l'accident uniquement.** Un accident à une intersection peut avoir une ligne par voie ; garder la première évite de dupliquer l'accident. La documentation BAAC indique que cette table décrit le lieu principal de l'accident.
- **`catr`, `surf`, `situ`** reprises telles quelles, **`vma` et `nbv`** converties en nombres.

**Conducteurs** (usagers avec `catu = 1`, résumés sur l'accident) :
- **`age_cond_max` :** 2023 moins l'année de naissance, puis l'âge du conducteur le plus âgé. La vulnérabilité augmente avec l'âge.
- **`part_cond_hommes` :** part d'hommes parmi les conducteurs. Une part plutôt qu'un code `sexe` permet de résumer plusieurs conducteurs en une valeur.
- **`part_cond_loisirs` :** part des conducteurs dont le trajet est « promenade, loisirs » (`trajet = 5`). Ce motif est associé aux week-ends et aux routes de campagne.
- **`part_cond_proteges` :** part des conducteurs portant une ceinture ou un casque. Un conducteur compte comme protégé si l'un de ses trois équipements (`secu1`, `secu2`, `secu3`) vaut 1 (ceinture) ou 2 (casque), et comme non protégé sinon. Il n'est pas compté si son équipement est « non déterminable » ou non renseigné.

**Véhicules** (table `vehicules`, résumés sur l'accident) :
- **`veh_vulnerable` :** les 31 codes `catv` regroupés en 4 catégories, du plus vulnérable au plus protégé ; on garde celle du véhicule le plus vulnérable de l'accident. 31 modalités, souvent rares, auraient créé autant de colonnes à l'encodage ; et c'est le véhicule le moins protégé qui détermine en général la gravité.

  | Groupe | Codes `catv` |
  |---|---|
  | `velo_edp` | 1 bicyclette, 50 et 60 EDP (trottinettes…), 80 vélo à assistance électrique |
  | `2rm_3rm` | 2 cyclomoteur, 30 à 34 scooters et motos, 35 et 36 quads, 41 à 43 trois-roues |
  | `vl_vu` | 3 voiturette, 7 voiture, 10 utilitaire |
  | `lourd` | 13 à 17 poids lourds et tracteurs routiers, 20 engin spécial, 21 tracteur agricole, 37 autobus, 38 autocar, 39 train, 40 tramway |
- **`choc_avant` :** au moins un véhicule a son point de choc initial à l'avant (`choc` = 1, 2 ou 3). Un choc par l'avant signale en général un véhicule qui roulait vers l'obstacle.
- **`manv_risquee` :** au moins un véhicule circulait à contresens (5), franchissait le terre-plein central (6), s'est déporté (13, 14) ou dépassait (17, 18). Les 27 codes de manœuvre sont résumés en celles qui traduisent une prise de risque ou une perte de contrôle.
- **`pieton_heurte` :** au moins un véhicule a heurté un piéton (`obsm = 1`).

**Colonnes écartées :**

| Raison | Colonnes |
|---|---|
| Identifiants ou texte libre | `Num_Acc`, `id_usager`, `id_vehicule`, `num_veh`, `adr`, `voie` |
| Inutilisables | `an` (toujours 2023), `com` (11 311 communes), `pr`, `pr1`, `v1` (repères routiers) |
| Trop de manquants (69 à 100 %) | `lartpc`, `occutc`, `v2`, `larrout` ; `secu3` n'est utilisée que pour compléter `part_cond_proteges` |
| Remplacées par une variable construite | `hrmn`, `jour`, `mois`, `an_nais`, `sexe`, `trajet`, `secu1`, `secu2`, `catv`, `choc`, `manv`, `obsm` |
| Rendues inutiles par le passage à l'accident | `catu`, `place`, `grav` (remplacée par la cible), et `locp`, `actp`, `etatp`, qui ne concernent que les piétons |
| Non retenues pour rester sous 20 variables, à réévaluer | `dep`, `lat`, `long`, `circ`, `vosp`, `prof`, `plan`, `infra`, `obs`, `senc`, `motor` |

### 6. Préparation dans le notebook
- **Typage :** les 9 colonnes de codes (`lum`… `situ`, `veh_vulnerable`) sont lues comme du texte puis converties en catégories, pour qu'aucun modèle ne les traite comme des nombres (le code 4 de `lum` n'est pas « deux fois » le code 2). Le texte est lu au format Python classique, car le format texte de pandas code les manquants d'une façon que scikit-learn ne gère pas.
- **Test set mis de côté dès le chargement :** 20 % des accidents, stratifiés sur `grav_max`, avec `random_state=42`. Toute l'exploration et tous les apprentissages (imputation, encodage…) se font sur le train, pour ne pas biaiser l'évaluation finale (*data snooping*, chapitre 02 du cours).
- **Imputation des valeurs manquantes,** apprise sur le train seul :
  - **`vma` :** médiane selon `agg`, soit 80 km/h hors agglomération et 50 km/h en agglomération, avec un indicateur `vma_manquant`. Une valeur unique serait fausse pour l'un des deux groupes.
  - **Autres numériques :** médiane, avec un indicateur de manquant. Quand l'âge ou le motif du trajet manque, les accidents sont nettement moins graves : la colonne indicatrice garde cette information, que la médiane seule effacerait.
  - **Catégorielles :** valeur la plus fréquente, sans indicateur, car elles ont moins de 0,5 % de manquants.

## Structure
- `notebooks/` : notebooks (01 = exploration)
- `src/` : scripts utilitaires
- `data/raw/` (ignoré par git), `data/processed/` : données
- `reports/figures/` : figures exportées
