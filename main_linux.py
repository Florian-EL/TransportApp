from cx_Freeze import setup, Executable

build_exe_options = {
    "include_files": [
        ("src", "src")
    ],
}

setup(
    name="TransportApp",
    version="2.0",
    description="Application de gestion de transport",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            script="main.py",
            base=None,
            icon="src/assets/app_icon.ico",
            target_name="TransportApp"
        )
    ]
)
