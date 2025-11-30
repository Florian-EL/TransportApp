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
- **Grpahique de statistique sur onglet en cours** : Affichage de graphiques qui résume les stats par transport
- **Lancement par fichier executable** : Propreté de l'application
- **Personalisation de l'interface** : Beauté de l'application

## Fonctionnalités à venir :
- **Multilangue (anglais et français)** : Adapter l'application pour plusieurs langues
- **Ajout d'un onglet statistiques** : Permettre des statistiques plus générale entre transports et années
D'autres fonctionnalités seront à venir

## Installation
### Prérequis
- Python 3.10
- `pip` installé
- librairies du requirements.txt

## Utilisation
Lancez l'application avec :
```bash
python main.py
```
Ou construisez un executable windows :
'''bash
python build.exe build
'''

## Structure du projet
```
TransportApp/
│── src/
│   ── TransportApp.py
│   ── AddDataDialog.py
│   ── DelDataDialog.py
│   ── FilterHeaderView.py
|   ── StatsWidget.py
│── data/
│── main.py
│── build.py
│── style.css
│── README.md
│── requirements.txt
```

## Licence
Ce projet est sous licence **MIT**. Voir le fichier `LICENSE` pour plus d’informations.

## Auteur
**Florian** - Idée, Développement & Conception

---
*Ce projet est en cours de développement !*

