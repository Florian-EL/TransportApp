# TransportApp

## Description
TransportApp est une application permettant de visualiser, filtrer et analyser ses données de déplacement.
L'application propose une interface graphique basée sur **PyQt5**.


## Fonctionnalités actuelles :
## *Current functionnalities :*
- **Chargement de fichiers CSV** : Importer des données de transport.
- **Affichage sous forme de tableau** : Visualiser les données dans des onglets.
- **Filtrage et triage dynamique** : Rechercher des valeurs spécifiques par colonne.
- **Statistiques par type de transport** : Génération d'un tableur récapitutif des statistiques annuelles
- **Grpahique de statistique sur onglet en cours (en cours)** : Affichage de graphiques qui résume les stats par transport

## Fonctionnalités à venir :
- **Multilangue (anglais et français)** : Adapter l'application pour plusieurs langues
- **Lancement par fichier executable** : Propreté de l'application (fondamentalement pas le plus important)
- **Ajout de graphique de statistiques sur chaque onglet** : Permettre une première étape de statistiques par type de transport
- **Ajout d'un onglet statistiques** : Permettre des statistiques plus générale entre transports et années
D'autres fonctionnalités seront à venir

## Installation
### Prérequis
- Python 3.10
- `pip` installé

## Utilisation
Lancez l'application avec :
```bash
python main.py
```

## Structure du projet
```
TransportApp/
│── src/
│   ── main.py
│   ── AddDataDialog.py
│   ── FilterHeaderView.py
|   ── StatsWidget.py
│── data/
│── setup.py #may work one day
│── style.css #for the future
│── README.md
│── requirement.txt #to be modified
```

## Licence
Ce projet est sous licence **MIT**. Voir le fichier `LICENSE` pour plus d’informations.

## Auteur
**Florian** - Développement & Conception

---
*Ce projet est en cours de développement !*

