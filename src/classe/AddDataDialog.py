import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QDialog, QLineEdit

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
            input_field = QLineEdit()
            input_field.setPlaceholderText(col)
            self.inputs[col] = input_field
            self.layout.addWidget(input_field)

        # Bouton pour valider
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_data)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)
    
    def save_to_file(self):
        """Sauvegarde les données pour chaque onglet."""
        for key, file_path in self.parent().file_paths.items():
            if key == self.key:
                data_to_save = self.data
                data_to_save.to_csv(file_path, index=False, sep=";")

    def add_data(self):
        """Ajoute une nouvelle ligne au DataFrame."""
        try:
            new_data = pd.DataFrame([{col: self.inputs[col].text() for col in self.donneebrut.columns}])
            
            self.data = pd.concat([self.donneebrut, new_data], ignore_index=True)
            if self.key != 'Marche' :
                self.data['Date'] = pd.to_datetime(self.data['Date'], format='%d/%m/%Y')
                self.data.sort_values(by='Date', ascending=False, inplace=True)
                self.data['Date'] = self.data['Date'].dt.strftime('%d/%m/%Y')
            
            self.save_to_file()
            
            if self.key == "Fiesta" :
                self.parent().calculate_fiesta(self.data)
                self.parent().convert_to_number(self.key, self.data)
            elif self.key == 'Marche' :
                self.parent().calculate_marche(self.data)
            else :
                self.parent().convert_to_number(self.key, self.data)
            
            self.parent().data[self.key] = self.data
            
            self.parent().update_table(self.key, self.parent().data[self.key])
            self.parent().update_stats_table(self.key, self.parent().data[self.key])
            
            self.close()
            
        except Exception as e:
            error_msg = QLabel(f"Erreur: {str(e)}")
            self.layout.addWidget(error_msg)
