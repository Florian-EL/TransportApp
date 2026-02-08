import pandas as pd
from pathlib import Path
from typing import Dict, Optional

from src.classe.utils import convert_to_number, calculate_fiesta, calculate_marche


class DataManager():
    def __init__(self, file_paths: Dict[str, Path], aux_paths: Optional[Dict[str, Path]] = None):

        self.file_paths = file_paths
        self.aux_file_paths = aux_paths or {}
        
        self.data: Dict[str, pd.DataFrame] = {k: self._load(p) for k, p in self.file_paths.items()}
        
        self.aux: Dict[str, pd.DataFrame] = {k : self._normalize_aux_df(self._load(p)) for k, p in self.aux_file_paths.items()}

    def _normalize_aux_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy(deep=True)
        df['Année'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.year        
        df['Prix (€)'] = pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0)
        return df

    def _load(self, path: Path) -> pd.DataFrame:
        try:
            return pd.read_csv(path, delimiter=";")
        except FileNotFoundError:
            # colonnes génériques si fichier absent
            return pd.DataFrame(columns=["Date", "Type", "Distance (km)", "Heures", "Minutes", "Prix (€)", "CO2 (kg)"])

    def save(self, key: str):
        path = self.file_paths[key]
        df = self.data.get(key)
        if df is not None and 'Abonnement' in df.columns:
            mask = df['Abonnement'].astype(str).str.lower().isin(["true", "1", "yes"])
            if 'Prix (€)' not in df.columns:
                df['Prix (€)'] = 0
            df.loc[mask, 'Prix (€)'] = 0
            self.data[key] = df
        self.data[key].to_csv(path, sep=';', index=False)

    def save_R(self, key: str):
        # Sauvegarde d'un fichier annexe
        if key in self.aux_file_paths:
            path = self.aux_file_paths[key]
            self.aux[key].to_csv(path, sep=';', index=False)

    def get(self, key: str) -> pd.DataFrame:
        # retourne une copie pour éviter mutation directe
        return self.data[key].copy(deep=True)

    def get_R(self, key: str) -> pd.DataFrame:
        return self.aux.get(key, pd.DataFrame()).copy(deep=True)

    def set(self, key: str, df: pd.DataFrame):
        self.data[key] = df.copy(deep=True)

    def set_R(self, key: str, df: pd.DataFrame):
        self.aux[key] = df.copy(deep=True)
        # exposer aussi dans data
        self.data[key] = self._normalize_aux_df(self.aux[key])

    def apply_transformations(self, key: str):
        # appliquer transformations uniquement aux données principales
        if key in self.aux : return
        
        df = self.data[key]
        if key == "Fiesta":
            df = calculate_fiesta(df)
            df = convert_to_number(key, df)
        elif key == "Marche":
            df = calculate_marche(df)
        else:
            df = convert_to_number(key, df)

        # Prise en compte des abonnements : si la table principale contient les colonnes
        # 'Abonnement' et 'ID', remplacer les prix nuls (0) par le prix unitaire dérivé
        # depuis la table annexe correspondante (_R) divisée par le nombre de trajets
        # ayant cet abonnement (par ID).
        # Toujours créer une colonne de prix appliqué qui reflète le prix utilisé
        # pour les calculs (sans modifier la colonne 'Prix (€)' originale qui vient du CSV).
        
        df['Prix appliqué (€)'] = pd.to_numeric(df.get('Prix (€)', 0), errors='coerce').fillna(0)

        if 'Abonnement' in df.columns and 'ID' in df.columns and not df.empty:
            # Normaliser Abonnement en bool
            df['Abonnement'] = df['Abonnement'].astype(str).str.lower().isin(["true", "1", "yes"])
            
            # Nombre de trajets par ID où Abonnement est True
            if key == "Métro" :
                
                df_b = convert_to_number("Bus", self.data["Bus"])
                df_b['Abonnement'].astype(str).str.lower().isin(["true"])
                
                s1 = df[df['Abonnement']]['ID'].value_counts()
                s2 = df_b[df_b['Abonnement']]['ID'].value_counts()
                
                trip_counts = s1.add(s2, fill_value=0).astype(int)
            
            elif key == "Bus" :           
                df_m = convert_to_number("Métro", self.data["Métro"])
                df_m['Abonnement'].astype(str).str.lower().isin(["true"])
                
                s1 = df[df['Abonnement']]['ID'].value_counts()
                s2 = df_m[df_m['Abonnement']]['ID'].value_counts()
                
                trip_counts = s1.add(s2, fill_value=0).astype(int)
            else :
                trip_counts = df[df['Abonnement']]['ID'].value_counts()

            if not trip_counts.empty:
                # Construire un lookup {ID: dernier_prix} à partir des tables annexes qui concernent ce mode
                price_lookup = {}
                for aux_key, aux_df in self.aux.items():
                    # associer les annexes dont le nom contient la clé principale (cas-insensible)
                    if key.lower() in aux_key.lower():
                        if 'ID' in aux_df.columns and 'Prix (€)' in aux_df.columns:
                            aux = aux_df.copy()
                            # parser la date si présente pour choisir le prix le plus récent
                            aux['__dt'] = pd.to_datetime(aux.get('Date', None), dayfirst=True, errors='coerce')
                            aux.sort_values(by='__dt', ascending=False, inplace=True)
                            for _, row in aux.iterrows():
                                aid = row.get('ID')
                                if pd.isna(aid):
                                    continue
                                # ne remplir que si on n'a pas déjà un prix pour cet ID
                                if aid not in price_lookup:
                                    p = pd.to_numeric(row.get('Prix (€)'), errors='coerce')
                                    if pd.notna(p):
                                        price_lookup[aid] = float(p)

                # Appliquer la division du prix par le nombre de trajets pour chaque ID
                for aid, cnt in trip_counts.items():
                    try:
                        price = price_lookup.get(aid)
                        if price is None or pd.isna(price) or int(cnt) == 0:
                            continue
                        unit = float(price) / int(cnt)
                        # Mettre à jour uniquement les lignes Abonnement True et Prix == 0 (prix original)
                        mask = (df['ID'] == aid) & (df['Abonnement']) & (
                            pd.to_numeric(df.get('Prix (€)'), errors='coerce').fillna(0) == 0)
                        df.loc[mask, 'Prix appliqué (€)'] = round(unit, 2)
                    except Exception:
                        # ignorer les IDs posant problème
                        continue

        # Recalculer les indicateurs liés au prix (prix horaire, prix au km) en se basant
        # sur la colonne 'Prix appliqué (€)'. On suppose que 'Heures','Minutes' et 'Distance (km)'
        # ont été normalisés par convert_to_number précédemment.

        df['Prix appliqué (€)'] = pd.to_numeric(df['Prix appliqué (€)'], errors='coerce').fillna(0)
        # éviter division par zéro
        hours = df['Heures'] + df['Minutes'] / 60
        df['Prix horaire (€)'] = round((df['Prix appliqué (€)'] / hours).replace([pd.NA, float('inf'), float('-inf')], 0).fillna(0).astype(float), 2)
        df['Prix au km (km)'] = round((df['Prix appliqué (€)'] / df['Distance (km)']).replace([pd.NA, float('inf'), float('-inf')], 0).fillna(0).astype(float), 2)

        self.data[key] = df

    # API utilitaire : concat de toutes les données pour stats
    def concat_all(self) -> pd.DataFrame:
        # On concatène toutes les dataframes exposées dans self.data.
        # Les annexes ont été normalisées pour fournir au moins 'Année' et 'Prix (€)'.
        if not self.data:
            return pd.DataFrame()
        return pd.concat(self.data.values(), ignore_index=True, sort=False).copy()