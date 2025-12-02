import pandas as pd
from pathlib import Path

from src.classe.utils import convert_to_number, calculate_fiesta, calculate_marche

class DataManager():
    def __init__(self, file_paths : dict):
        self.file_paths = file_paths
        self.data = {k: self._load(p) for k, p in self.file_paths.items()}

    def _load(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_csv(path, delimiter=";")
        except FileNotFoundError:
            return pd.DataFrame(columns=["Date", "Type", "Distance", "Heures", "Minutes", "Prix", "CO2"])

    def save(self, key: str):
        path = self.file_paths[key]
        self.data[key].to_csv(path, sep=";", index=False)

    def get(self, key: str) -> pd.DataFrame:
        # retourne une copie pour éviter mutation directe
        return self.data[key].copy(deep=True)

    def set(self, key: str, df: pd.DataFrame, save: bool = True):
        self.data[key] = df.copy(deep=True)
        if save:
            self.save(key)

    def apply_transformations(self, key: str):
        df = self.data[key]
        if key == "Fiesta":
            df = calculate_fiesta(df)
            df = convert_to_number(key, df)
        elif key == "Marche":
            df = calculate_marche(df)
        else:
            df = convert_to_number(key, df)
        self.data[key] = df

    # API utilitaire : concat de toutes les données pour stats
    def concat_all(self) -> pd.DataFrame:
        return pd.concat(self.data.values(), ignore_index=True).copy()