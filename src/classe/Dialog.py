from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QComboBox
import pandas as pd

class AddDataDialog(QDialog):
    """Fenêtre pour ajouter des données."""
    def __init__(self, key, donneebrut, parent=None):
        super().__init__(parent)
        self.key = key
        self.donneebrut = donneebrut
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
            # sauf pour les clés auxiliaires se terminant par "_R" : dans ce cas, utiliser un champ texte simple
            if col == 'ID':
                if self.key.endswith('_R'):
                    # champ texte simple pour les données auxiliaires
                    input_field = QLineEdit()
                    input_field.setPlaceholderText(col)
                    self.inputs[col] = input_field
                    self.layout.addWidget(input_field)
                    continue

                combo = QComboBox()
                combo.setEditable(True)
                try:
                    ids = ["0"]
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
            
            for d in self.data :
                if 'Prix (€)' in str(d).lower() and 'Abonnement' in self.data.columns:
                    mask = (self.data['Abonnement'] == True) | (self.data['Abonnement'].astype(str).str.lower().isin(['true', '1', 'yes', 'y']))
                    self.data.loc[mask, d] = 0

            if self.key.endswith('_R') :
                self.parent().dm.set_file_R(self.key, self.data)
                self.parent().dm.save_R(self.key)
            else :
                self.parent().dm.set_file(self.key, self.data)
                self.parent().dm.save(self.key)
                
            
            self.close()
            
        except Exception as e:
            error_msg = QLabel(f"Erreur: {str(e)}")
            self.layout.addWidget(error_msg)
            raise ValueError(e)



class DelDataDialog(QDialog):
    """Fenêtre pour supprimer une ligne en fonction de certains champs."""
    def __init__(self, key, df, parent=None):
        super().__init__(parent)
        self.key = key
        self.df = df
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

            data = self.df.drop(index=matching_rows.index[0]).reset_index(drop=True)

            if self.key.endswith('_R') :
                raw = self.parent().dm.get_R(self.key)
            else :
                raw = self.parent().dm.get(self.key)

            # appliquer la suppression sur le RAW
            raw = raw.drop(index=matching_rows.index[0]).reset_index(drop=True)
            
            
            if self.key.endswith('_R') :
                self.parent().dm.set_file_R(self.key, data)
                self.parent().dm.save_R(self.key)
            else :
                self.parent().dm.set_file(self.key, data)
                self.parent().dm.save(self.key)
                
            
            self.close()
            
        except ValueError as ve:
            self.error_label.setText(f"Erreur : {str(ve)}")
            print(ve)
        except Exception as e:
            self.error_label.setText(f"Erreur inattendue : {str(e)}")
            print(e)