from setuptools import setup, find_packages
import py2exe

import sys
sys.setrecursionlimit(5000)  # Augmente la limite (valeur à ajuster si besoin)

setup(
    name="TransportApp",
    version="1.0",
    #windows/console
    windows=["src/main.py"],  # Remplace par le chemin correct
    packages=["src/classe", "src/data"],  # Liste des dossiers nécessaires
    options={
        "py2exe": {
            "includes": [],  # Ajoute ici les modules supplémentaires si nécessaire
            "bundle_files": 1,  # Tout inclure dans un seul fichier EXE
            "compressed": True,  # Compression de l'exécutable
        }
    },
    #zipfile=None,  # Évite un fichier .zip externe
)