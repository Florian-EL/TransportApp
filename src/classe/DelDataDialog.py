import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QDialog, QLineEdit, QHBoxLayout

class DelDataDialog(QDialog):
    """Fenêtre pour supprimer une ligne en fonction de certains champs."""
    def __init__(self, key, df, parent=None):
        super().__init__(parent)
        self.key = key
        self.df = df
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

    def del_data(self, key):
        """Supprime une ligne du DataFrame en fonction des champs remplis."""
        try:
            # Construire un masque pour filtrer les lignes
            mask = pd.Series(True, index=self.df.index)
            for col, input_field in self.inputs.items():
                value = input_field.text().strip()
                if value:  # Si un champ est rempli
                    mask &= self.df[col].astype(str) == value

            # Vérifier si une seule ligne correspond
            matching_rows = self.df[mask]
            if len(matching_rows) == 0:
                raise ValueError("Aucune ligne ne correspond aux critères.")
            elif len(matching_rows) > 1:
                raise ValueError("Plusieurs lignes correspondent aux critères. Veuillez préciser davantage.")

            self.df = self.df.drop(index=matching_rows.index[0]).reset_index(drop=True)

            # Mettre à jour le DataFrame dans le parent
            self.parent().data[self.key] = self.df
            
            self.parent().apply_transformations(self.key)
            
            # Sauvegarder les modifications
            self.parent().save_to_file()

            # Fermer la fenêtre
            self.close()
            
            
            
            
        except ValueError as ve:
            self.error_label.setText(f"Erreur : {str(ve)}")
        except Exception as e:
            self.error_label.setText(f"Erreur inattendue : {str(e)}")