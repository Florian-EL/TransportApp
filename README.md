# TransportApp

Application de bureau pour consulter et analyser des données personnelles de déplacement. Elle affiche les trajets par mode de transport, permet de filtrer les tableaux et calcule des indicateurs de coût, de durée, de distance et d’émissions. L’interface utilise PyQt5 ; les données sont manipulées avec pandas et présentées sous forme de tableaux et de graphiques.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Modes et données](#modes-et-données)
- [Technologies](#technologies)
- [Installation et lancement](#installation-et-lancement)
- [Configuration des fichiers de données](#configuration-des-fichiers-de-données)
- [Format des CSV](#format-des-csv)
- [Structure du projet](#structure-du-projet)
- [Construction sous Linux](#construction-sous-linux)
- [Dépannage](#dépannage)

## Fonctionnalités

- Affichage des déplacements dans des onglets par mode de transport.
- Tri et filtres de colonnes dans les tableaux.
- Calcul et affichage d’indicateurs tels que distance, durée, coût et CO₂, avec des valeurs dérivées (coût horaire et coût au kilomètre).
- Traitement dédié de certains modes comme la marche et Fiesta.
- Gestion des abonnements : les fichiers auxiliaires peuvent fournir un prix réparti sur les trajets associés.
- Tableaux récapitulatifs statistiques et graphiques pour les données affichées et les années.
- Chargement et sauvegarde des données au format CSV séparé par point-virgule.

## Modes et données

Les catégories principales utilisées par l’application sont Train, Métro, Bus, Fiesta, Avion, Taxi, Marche et Vélo. Des fichiers auxiliaires peuvent compléter certains modes : `train_R`, `metro_bus_R`, `fiesta_R` et `taxi_R`.

Le dépôt comprend des CSV d’exemple sous `data/` et des fichiers de données sous `Data/`. Le fichier `src/assets/file.json` indique les chemins à charger. Dans la configuration actuellement fournie, ces chemins pointent vers `/home/florian/Documents/Data/`, donc ils devront généralement être modifiés pour une autre machine. Les fichiers d’exemple du dépôt ne sont pas automatiquement chargés par cette configuration.

## Technologies

- Python 3.13
- PyQt5 5.15.11
- pandas 2.2.3
- matplotlib 3.10.1
- cx_Freeze pour la création du programme Linux

Les dépendances Python sont listées dans `requirements.txt`.

## Installation et lancement

Depuis la racine du dépôt, créez un environnement virtuel et installez les dépendances :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Lancement de l’application :

```bash
python main.py
```

Le point d’entrée crée l’application Qt, affiche la fenêtre principale et charge les ressources référencées par `src/assets/file.json`.

## Configuration des fichiers de données

Éditez `src/assets/file.json` avant le premier lancement sur une nouvelle machine. La clé `data_files` contient huit chemins, dans l’ordre attendu par l’application : train, métro, bus, Fiesta, avion, taxi, marche et vélo. La clé `aux_files` référence les fichiers annexes utilisés notamment pour le calcul des prix d’abonnement.

Utilisez des chemins valides et accessibles. Les chemins absolus fournis dans le dépôt sont propres à l’environnement d’origine. Le `DataManager` lit les fichiers CSV avec le séparateur `;`. Si un fichier principal est absent, un tableau vide avec des colonnes génériques est créé ; cela permet le démarrage mais ne charge pas les exemples automatiquement.

## Format des CSV

Les fichiers doivent être encodés dans un format lisible par pandas et utiliser le point-virgule comme séparateur. Les colonnes exactes varient selon le mode, mais les calculs utilisent notamment des champs comme `Date`, `Départ`, `Arrivée`, `Heures`, `Minutes`, `Distance (km)`, `Prix (€)` et `CO2 (kg)`. Les fichiers avec abonnement peuvent aussi utiliser `Abonnement` et `ID`.

Les exemples de trajets sont disponibles dans `data/exemple_bus.csv`, `data/exemple_metro.csv` et `data/exemple_train.csv`. Vérifiez leur structure avant de les ajouter aux chemins de configuration.

## Structure du projet

```text
TransportApp/
├── main.py                   # Point d’entrée PyQt5
├── QT_Transport.py           # Fenêtre principale et assemblage des onglets
├── requirements.txt          # Dépendances Python
├── build_linux.sh            # Construction et raccourci Linux
├── Data/                     # Jeux CSV présents dans le dépôt
├── data/                     # Exemples CSV
├── src/
│   ├── assets/               # Configuration JSON, styles et icône
│   └── classe/
│       ├── DataManager.py    # Chargement, sauvegarde et calculs
│       ├── Dialog.py         # Boîtes de dialogue d’ajout/suppression
│       ├── FilterHeaderView.py # Filtres et tri des tableaux
│       ├── Graph.py          # Statistiques et graphiques
│       └── utils.py          # Fonctions de normalisation/calcul
└── src_old/                  # Anciennes versions, non utilisées par le lancement courant
```

## Construction sous Linux

Le dépôt fournit `main_linux.py` et `build_linux.sh` pour construire et installer le raccourci desktop. Le script utilise cx_Freeze : installez-le dans l’environnement Python actif avant de l’exécuter.

```bash
python -m pip install cx_Freeze
./build_linux.sh
```

Le script supprime le répertoire `build/`, construit l’application et copie le fichier `.desktop` vers `~/.local/share/applications/`. Il contient des chemins absolus à adapter si le dépôt n’est pas situé dans `/home/florian/TransportApp`. La construction est prévue pour Linux ; les paramètres de la configuration doivent être adaptés pour cibler Windows ou un autre système.

## Dépannage

- **Les tableaux sont vides** : vérifiez les chemins `data_files` dans `src/assets/file.json` et confirmez qu’ils ciblent les bons CSV.
- **Les caractères ou colonnes sont mal lus** : contrôlez l’encodage et le séparateur `;` des fichiers.
- **Erreur de dépendance** : vérifiez que l’environnement virtuel est activé puis réinstallez `requirements.txt`.
- **Prix d’abonnement absents ou incorrects** : vérifiez la présence des CSV auxiliaires, les colonnes `ID`, `Abonnement`, `Date` et `Prix (€)`, et la cohérence des identifiants.
