from cx_Freeze import setup, Executable
import sys
from PySide6.QtCore import QLibraryInfo

import cx_Freeze.hooks.qthooks as qthooks
qthooks.load_qt_qtqml = lambda *args, **kwargs: None

plugin_path = QLibraryInfo.path(QLibraryInfo.PluginsPath)

# Masquer la console pour une app GUI
base = "Win32GUI" if sys.platform == "win32" else None

build_exe_options = {
    "packages": ["matplotlib", "pandas", "PyQt5"],
    "include_files": [
        ("src", "src"),
        ("data", "data"),
        (plugin_path, "platform"),
        ("src/assets/app_icon.ico", "src/assets/app_icon.ico"),
        ("style.css", "style.css")
    ],
    "include_msvcr": True
}


setup(
    name="TransportApp",
    version="1.0",
    description="Application de gestion de transport",
    options={"build_exe": build_exe_options},
    executables=[Executable(script="main.py", base="Win32GUI", icon="src/assets/app_icon.ico", target_name="TransportApp.exe")]
)