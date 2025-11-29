from cx_Freeze import setup, Executable
import sys
from PySide6.QtCore import QLibraryInfo
import cx_Freeze.hooks.qthooks as qthooks
import os

# Désactive le chargement QML (évite certaines erreurs avec PySide6)
qthooks.load_qt_qtqml = lambda *args, **kwargs: None

# Récupère le chemin des plugins Qt
plugin_path = QLibraryInfo.path(QLibraryInfo.PluginsPath)

# Sur Linux, il n’y a pas de "Win32GUI"
# (base=None signifie application GUI sans console si gérée correctement)
base = None

# Options de build
build_exe_options = {
    "packages": ["matplotlib", "pandas", "PySide6"],
    "include_files": [
        ("src", "src"),
        (plugin_path, "platforms")
    ],
}

# Détermination du nom de l’exécutable selon le système
target_name = "TransportApp"
if sys.platform == "win32":
    target_name += ".exe"

# Configuration de l’application
setup(
    name="TransportApp",
    version="1.0",
    description="Application de gestion de transport",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            script="main.py",
            base=base,
            icon="src/assets/app_icon.ico",
            target_name=target_name
        )
    ]
)
