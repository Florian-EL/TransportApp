import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QDialog, QLineEdit

class AddDataDialog(QDialog):
    """Fenêtre pour ajouter des données."""
    def __init__(self, key, df, parent=None):
        super().__init__(parent)
        self.key = key
        self.df = df
        self.setWindowTitle(f"Ajouter des données ({key})")
        self.layout = QVBoxLayout()

        # Champs pour chaque colonne
        self.inputs = {}
        for col in self.df.columns:
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
            new_data = {col: self.inputs[col].text() for col in self.df.columns}
            self.df = pd.concat([self.df, pd.DataFrame([new_data])], ignore_index=True)
            self.parent().data[self.key] = self.df
            self.parent().update_table(self.key, self.df)
            self.close()
        except Exception as e:
            error_msg = QLabel(f"Erreur: {str(e)}")
            self.layout.addWidget(error_msg)
