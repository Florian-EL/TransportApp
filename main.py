import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QTabWidget, QFileDialog, QWidget, QLabel, QDialog, QLineEdit, QSizePolicy, QHeaderView, QTableView
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class TransportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file_paths = {"Train" : "data/train.csv",
                            "Bus" : "data/bus.csv",
                            "Metro" : "data/metro.csv"}
        self.data = {key: self.load_data(path) for key, path in self.file_paths.items()}
        self.models = {}
        self.tables = {}  # Associe les onglets aux tableaux
        self.stats_tables = {}  # Associe les onglets aux tableaux de statistiques
        self.proxy_models = {}
        self.filters = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Transport App")

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        button_layout = QHBoxLayout()

        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)

        for key in self.data.keys():
            self.convert_to_number(self.data[key])
            self.add_tab(key, self.data[key])

        self.new_window_button = QPushButton("Ajouter des données")
        self.load_button = QPushButton("Charger les données")
        self.save_button = QPushButton("Sauvegarder les données")

        self.new_window_button.clicked.connect(self.open_new_window)
        self.load_button.clicked.connect(self.load_from_file)
        self.save_button.clicked.connect(self.save_to_file)

        button_layout.addWidget(self.new_window_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)

        self.layout.addWidget(self.tabs)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)
        
    def convert_to_number(self, df):
        df['Heures'] = pd.to_numeric(df['Heures'], errors='coerce').fillna(0).astype(int)
        df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce').fillna(0).astype(int)
        df['Distance (km)'] = pd.to_numeric(df['Distance (km)'], errors='coerce').fillna(0).astype(int)
        df['Prix (€)'] = pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0).astype(int)
        df['CO2 (kg)'] = pd.to_numeric(df['CO2 (kg)'], errors='coerce').fillna(0).astype(int)

    def add_tab(self, key, df):
        def apply_filter(col, text):
            proxy_model.setFilterKeyColumn(col)
            proxy_model.setFilterRegularExpression(text)
        
        tab = QWidget()
        tab.layout = QVBoxLayout()
        
        # Tableur de statistiques (QTableWidget)
        stats_table_widget = QTableWidget()
        stats_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  
        stats_table_widget.resizeRowsToContents()
        stats_table_widget.setMaximumHeight(stats_table_widget.verticalHeader().height() + stats_table_widget.horizontalHeader().height())
        self.stats_tables[key] = stats_table_widget

        # Tableau principal (QTableView)
        model = QStandardItemModel()
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(model)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(-1)  # Appliquer à toutes les colonnes
        proxy_model.setDynamicSortFilter(True)
        proxy_model.sort(df.columns.get_loc("Date"), Qt.DescendingOrder)

        self.models[key] = model
        self.proxy_models[key] = proxy_model

        table_view = QTableView()
        table_view.setModel(proxy_model)
        table_view.setSortingEnabled(True)
        
        # Gestion filtre et header
        header = FilterHeaderView(table_view)
        table_view.setHorizontalHeader(header)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header.set_filter_callback(apply_filter)

        # Charger les données
        self.load_data_to_model(model, df)

        tab.layout.addWidget(stats_table_widget)
        self.update_statistics(key, df)

        tab.layout.addWidget(table_view)
        self.update_table(key, df)
        
        tab.setLayout(tab.layout)
        self.tabs.addTab(tab, key)

    def load_data_to_model(self, model, df):
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(df.columns)

        for row in df.itertuples(index=False):
            items = []
            for cell in row:
                item = QStandardItem(str(cell))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)  # Aligner en haut et à gauche
                items.append(item)
            model.appendRow(items)

    def create_filter(self, proxy_model, column_index):
        def filter_function(text):
            proxy_model.setFilterKeyColumn(column_index)
            proxy_model.setFilterFixedString(text)
        return filter_function

    def update_table(self, key, df):
        
        df["Prix horaire (€)"] = round(df["Prix (€)"] / (df["Heures"] + df["Minutes"] / 60), 2)
        df["Prix au km (km)"] = round(df["Prix (€)"] / df["Distance (km)"], 2)
        df["CO2 par km (g/km)"] = round(df["CO2 (kg)"] / df["Distance (km)"]*1000, 2)
        
        model = self.models[key]
        model.clear()
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(df.columns)

        for row in df.itertuples(index=False):
            items = [QStandardItem(str(cell)) for cell in row]
            model.appendRow(items)

        self.proxy_models[key].invalidateFilter()

    def update_statistics(self, key, df):
        """Calculer et afficher les statistiques par année."""
        
        # Calcul des statistiques : somme et moyenne
        stats = df.groupby('Année').agg({
            'Distance (km)': ['sum'],
            'Heures': ['sum'],
            'Minutes': ['sum'],
            'Prix (€)': ['sum'],
            'CO2 (kg)': ['sum']
        }).reset_index()
        
        #stats.columns = ['Année', 'Distance (km)', 'Heures', 'Minutes', 'Prix (€)', 'CO2 (kg)']
        stats['Heures'] = stats['Heures'] + stats['Minutes'] // 60
        stats['Minutes'] = stats['Minutes'] % 60
        stats['Prix horaire (€)'] = round(stats['Prix (€)'] / (stats['Heures'] + stats['Minutes'] / 60), 2)
        stats['Prix au km (km)'] = round(stats['Prix (€)'] / stats['Distance (km)'], 2)
        stats['CO2 par km (g/km)'] = round(stats['CO2 (kg)'] / stats['Distance (km)'] * 1000, 2)

        stats_table_widget = self.stats_tables[key]
        stats_table_widget.setRowCount(len(stats))
        stats_table_widget.setColumnCount(len(stats.columns))
        stats_table_widget.setHorizontalHeaderLabels(['Année', 'Distance (km)', 'Heures', 'Minutes', 'Prix (€)', 'CO2 (kg)', 
                                                      'Prix horaire (€)', 'Prix au km (km)', 'CO2 par km (g/km)'])
        stats_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i in range(len(stats)):
            for j in range(len(stats.columns)):
                value = str(stats.iloc[i, j])
                stats_table_widget.setItem(i, j, QTableWidgetItem(value))

    def load_data(self, file_path):
        """Charge les données depuis un fichier CSV."""
        try:
            return pd.read_csv(file_path, delimiter=";")
        except FileNotFoundError:
            return pd.DataFrame(columns=["Date", "Type", "Distance", "Heures", "Minutes", "Prix", "CO2"])

    def save_to_file(self):
        """Sauvegarde les données pour chaque onglet."""
        for key, file_path in self.file_paths.items():
            df = self.data[key]
            df.to_csv(file_path, index=False, sep=";")
        self.show_message("Données sauvegardées avec succès.")

    def load_from_file(self):
        """Charge un fichier CSV sélectionné par l'utilisateur."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier CSV", "", "CSV Files (*.csv)")
        if file_path:
            key = self.tabs.tabText(self.tabs.currentIndex())
            self.file_paths[key] = file_path
            self.data[key] = self.load_data(file_path)
            self.update_table(key, self.data[key])
            self.show_message("Données chargées avec succès.")

    def open_new_window(self):
        """Ouvre une fenêtre pour ajouter des données."""
        key = self.tabs.tabText(self.tabs.currentIndex())
        if key in self.data:
            self.new_window = AddDataDialog(key, self.data[key], self)
            self.new_window.exec_()  # Utilisation de exec_ pour les QDialog

    def show_message(self, message):
        """Affiche un message temporaire."""
        msg = QLabel(message)
        msg.setStyleSheet("color: green;")
        self.layout.addWidget(msg)
        QApplication.processEvents()

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

class FilterHeaderView(QHeaderView):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setSectionsClickable(True)
        self.filters = {}

    def set_filter_callback(self, filter_callback):
        """Définit le callback pour appliquer le filtre."""
        self.filter_callback = filter_callback

    def create_filter(self, col):
        """Crée un QLineEdit pour filtrer une colonne spécifique."""
        if col not in self.filters:
            filter_input = QLineEdit(self.parent())
            filter_input.setPlaceholderText("🔍")
            filter_input.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
            filter_input.setStyleSheet("border: none; background: transparent; font-size: 12px;")
            filter_input.textChanged.connect(lambda text: self.filter_callback(col, text))
            self.setFixedHeight(60)  # Ajuste la hauteur de l'en-tête

            self.filters[col] = filter_input

    def resizeEvent(self, event):
        """Redéfinit la taille des champs de filtre en fonction de la taille des colonnes."""
        super().resizeEvent(event)
        for col, filter_input in self.filters.items():
            rect = self.sectionViewportPosition(col)
            filter_input.setGeometry(rect, self.height() // 2, self.sectionSize(col), self.height() // 2)

    def paintSection(self, painter, rect, logicalIndex):
        """Dessine le titre + la boîte de filtre dans l'en-tête."""
        super().paintSection(painter, rect, logicalIndex)

        if logicalIndex in self.filters:
            filter_input = self.filters[logicalIndex]
            filter_input.setGeometry(rect.x(), rect.y() + rect.height() // 2, rect.width(), rect.height() // 2)
            filter_input.setVisible(True)
        else:
            self.create_filter(logicalIndex)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransportApp()
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())
