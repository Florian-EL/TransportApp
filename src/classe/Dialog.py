from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QComboBox
import pandas as pd

class AddDataDialog(QDialog):
    """Fenêtre pour ajouter des données."""
    def __init__(self, key, donneebrut, parent=None):
        super().__init__(parent)
        self.key = key
        self.donneebrut = donneebrut[key]
        self.data = pd.DataFrame()
        self.setWindowTitle(f"Ajouter des données ({key})")
        self.layout = QVBoxLayout()
        
        # Champs pour chaque colonne
        self.inputs = {}
        for col in self.donneebrut.columns:
            # Abonnement -> case à cocher True/False
            if col == 'Abonnement':
                cb = QCheckBox(col)
                cb.setChecked(False)
                self.inputs[col] = cb
                self.layout.addWidget(cb)
                continue

            # ID -> combobox pré-remplie avec les 5 derniers ID référencés dans la table annexe correspondante
            if col == 'ID':
                combo = QComboBox()
                combo.setEditable(True)
                try:
                    ids = []
                    base_key = self.key
                    # parcourir les annexes et récupérer les IDs récents
                    for aux_key, aux_df in getattr(self.parent(), 'dm').aux.items():
                        if base_key.lower() in aux_key.lower() and 'ID' in aux_df.columns:
                            tmp = aux_df.copy()
                            tmp['__dt'] = pd.to_datetime(tmp.get('Date', None), dayfirst=True, errors='coerce')
                            tmp.sort_values(by='__dt', ascending=False, inplace=True)
                            for val in tmp['ID'].fillna('').astype(str).tolist():
                                if val and val not in ids:
                                    ids.append(val)
                    # limiter aux 5 derniers
                    ids = ids[:5]
                    if ids:
                        combo.addItems(ids)
                except Exception:
                    pass
                self.inputs[col] = combo
                self.layout.addWidget(combo)
                continue

            # Par défaut : champ texte
            input_field = QLineEdit()
            input_field.setPlaceholderText(col)
            self.inputs[col] = input_field
            self.layout.addWidget(input_field)

        # Bouton pour valider
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_data)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)
    
    
    def add_data(self):
        """Ajoute une nouvelle ligne au DataFrame."""
        try:
            # Lire les valeurs depuis les widgets, en tenant compte des types (QLineEdit, QCheckBox, QComboBox)
            row = {}
            for col in self.donneebrut.columns:
                widget = self.inputs.get(col)
                value = None
                try:
                    from PyQt5.QtWidgets import QLineEdit as _QLineEdit, QCheckBox as _QCheckBox, QComboBox as _QComboBox
                    if isinstance(widget, _QLineEdit):
                        value = widget.text()
                    elif isinstance(widget, _QCheckBox):
                        value = widget.isChecked()
                    elif isinstance(widget, _QComboBox):
                        value = widget.currentText()
                    else:
                        # fallback: try attribute text()
                        value = getattr(widget, 'text', lambda: '')()
                except Exception:
                    # last-resort: string representation
                    try:
                        value = str(widget)
                    except Exception:
                        value = ''
                row[col] = value

            new_data = pd.DataFrame([row])
            
            self.data = pd.concat([self.donneebrut, new_data], ignore_index=True)
            if self.key != 'Marche' :
                self.data['Date'] = pd.to_datetime(self.data['Date'], format='%d/%m/%Y')
                self.data.sort_values(by='Date', ascending=False, inplace=True)
                self.data['Date'] = self.data['Date'].dt.strftime('%d/%m/%Y')
                
            self.parent().dm.set(self.key, self.data)
            self.parent().dm.save(self.key)
            
            self.parent().dm.apply_transformations(self.key[:-2] if isinstance(self.key, str) and self.key.endswith("_R") else self.key)
            self.data = self.parent().dm.get(self.key)
            
            self.data.rename(columns=lambda x: x.replace('Prix (€)', 'Prix appliqué (€)'), inplace=False)
                    
            aux_to_load = self.data.copy()
            aux_cfg = self.parent().fixed_column_config.get(self.key) or self.parent().fixed_column_config.get(self.key + '')
            if aux_cfg:
                acols = [c for c in aux_cfg.get('visible', []) if c in aux_to_load.columns]
                if acols:
                    aux_to_load = aux_to_load[acols].copy()
                    if aux_cfg.get('rename'):
                        aux_to_load.rename(columns=aux_cfg.get('rename', {}), inplace=True)
            
            
            self.parent().data[self.key] = aux_to_load
            
            self.parent().update_table(self.key, self.parent().data[self.key])
            self.parent().update_stats_table(self.key, self.parent().data[self.key])
            self.parent().update_stats_tab(self.key, self.parent().data[self.key])
            
            self.close()
            
        except Exception as e:
            error_msg = QLabel(f"Erreur: {str(e)}")
            self.layout.addWidget(error_msg)



class DelDataDialog(QDialog):
    """Fenêtre pour supprimer une ligne en fonction de certains champs."""
    def __init__(self, key, df, parent=None):
        super().__init__(parent)
        self.key = key
        self.df = df[key]
        self.data = pd.DataFrame()
        self.setWindowTitle(f"Supprimer une ligne ({key})")
        self.layout = QVBoxLayout()
        
        # Champs dynamiques pour chaque colonne
        self.inputs = {}
        self.layout.addWidget(QLabel("Remplissez un ou plusieurs champs pour identifier la ligne à supprimer :"))
        for col in self.df.columns:
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Valeur pour {col}")
            self.inputs[col] = input_field
            self.layout.addWidget(input_field)
        
        # Bouton pour valider
        self.del_button = QPushButton("Supprimer")
        self.del_button.clicked.connect(self.del_data)
        self.layout.addWidget(self.del_button)

        # Zone pour afficher les erreurs
        self.error_label = QLabel("")
        self.layout.addWidget(self.error_label)

        self.setLayout(self.layout)
    
    def del_data(self):
        """Supprime une ligne du DataFrame en fonction des champs remplis."""
        try:
            # Construire un masque pour filtrer les lignes
            mask = pd.Series(True, index=self.df.index)
            for col, widget in self.inputs.items():
                value = widget.text().strip()
                if value:
                    mask &= self.df[col].astype(str) == value

            # Vérifier si une seule ligne correspond
            matching_rows = self.df[mask]
            if len(matching_rows) == 0:
                raise ValueError("Aucune ligne ne correspond aux critères.")
            elif len(matching_rows) > 1:
                raise ValueError("Plusieurs lignes correspondent aux critères. Veuillez préciser davantage.")

            self.data = self.df.drop(index=matching_rows.index[0]).reset_index(drop=True)

            # récupérer le CSV brut
            raw = pd.read_csv(self.parent().dm.file_paths[self.key], sep=';')

            # appliquer la suppression sur le RAW
            raw = raw.drop(index=matching_rows.index[0]).reset_index(drop=True)

            # écrire UNIQUEMENT le RAW
            raw.to_csv(self.parent().dm.file_paths[self.key], sep=';', index=False)

            # recharger proprement
            self.parent().dm.data[self.key] = raw
            self.parent().dm.apply_transformations(self.key)

            self.data = self.parent().dm.get(self.key)
            
            self.data.rename(columns=lambda x: x.replace('Prix (€)', 'Prix appliqué (€)'), inplace=False)
            
            aux_to_load = self.data.copy()
            aux_cfg = self.parent().fixed_column_config.get(self.key) or self.parent().fixed_column_config.get(self.key + '')
            if aux_cfg:
                acols = [c for c in aux_cfg.get('visible', []) if c in aux_to_load.columns]
                if acols:
                    aux_to_load = aux_to_load[acols].copy()
                    if aux_cfg.get('rename'):
                        aux_to_load.rename(columns=aux_cfg.get('rename', {}), inplace=True)
            
            
            self.parent().data[self.key] = aux_to_load
            
            self.parent().update_table(self.key, self.parent().data[self.key])
            self.parent().update_stats_table(self.key, self.parent().data[self.key])
            self.parent().update_stats_tab(self.key, self.parent().data[self.key])

            self.close()
            
        except ValueError as ve:
            self.error_label.setText(f"Erreur : {str(ve)}")
        except Exception as e:
            self.error_label.setText(f"Erreur inattendue : {str(e)}")