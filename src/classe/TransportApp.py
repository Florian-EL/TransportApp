import pandas as pd
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,\
                            QPushButton, QTabWidget, QFileDialog, QWidget, QLabel, QSizePolicy, QHeaderView, QTableView

from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from src.classe.FilterHeaderView import FilterHeaderView
from src.classe.AddDataDialog import AddDataDialog
from src.classe.StatsWidget import StatsWidget

class TransportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file_paths = {
            "Train" : "data/train.csv",
            "Metro" : "data/metro.csv",
            "Bus" :   "data/bus.csv",
            "Fiesta" :"data/fiesta.csv",
            "Avion" : "data/avion.csv",
            "Taxi" :  "data/taxi.csv",
        }
        self.data = {key: self.load_data(path) for key, path in self.file_paths.items()}
        self.models = {}
        self.tables = {}
        self.stats_tables = {}
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
            if key == "Fiesta" :
                self.calculate_fiesta(self.data[key])
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
    
    def calculate_fiesta(self, df) :
        v_moy = 35 #km/h
        nb_h_tot = 23280 #h
        temps_th_volant = 445 #h
        temps_vol_pourcent = 1.912 #%
        co2 = 0.105 #kg/km
        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
        df.sort_values(by='Date', ascending=False)
        df['Kilométrage (km)'].astype(int)

        df['Distance (km)'] = df['Kilométrage (km)'].shift(-1) - df['Kilométrage (km)']
        
        df['Litre par 100km'] =  round(pd.to_numeric(df['Quantité (L)'] / df['Distance (km)']*100).fillna(0).astype(float), 2)
        df['Prix au litre'] = round(pd.to_numeric(df['Prix (€)'] / df['Quantité (L)']).fillna(0).astype(float), 4)

        df['km journalier moy'] = round(pd.to_numeric(df['Distance (km)'] / (pd.to_datetime(df['Date']).shift(-1) - pd.to_datetime(df['Date'])).dt.days), 2)
        
        df['Heures'] = df['Distance (km)'] / v_moy
        df['Minutes'] = 0
        df['CO2 (kg)'] = co2 * df['Distance (km)']
    
    def convert_to_number(self, df):
        df['Heures'] = pd.to_numeric(df['Heures'], errors='coerce').fillna(0).astype(int)
        df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce').fillna(0).astype(int)
        df['Distance (km)'] = pd.to_numeric(df['Distance (km)'], errors='coerce').fillna(0).astype(float)
        df['Prix (€)'] = pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0).astype(float)
        df['CO2 (kg)'] = pd.to_numeric(df['CO2 (kg)'], errors='coerce').fillna(0).astype(float)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
        df.sort_values(by='Date', ascending=False, inplace=True)
        df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
        df['Année'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.year

    def add_tab(self, key, df):
        def apply_filter(col, text):
            proxy_model.setFilterKeyColumn(col)
            proxy_model.setFilterRegularExpression(text)
        
        def load_data_to_model(model, df):
            model.setColumnCount(len(df.columns))
            model.setHorizontalHeaderLabels(df.columns)

            for row in df.itertuples(index=False):
                items = []
                for cell in row:
                    item = QStandardItem(str(cell))
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)  # Aligner en haut et à gauche
                    items.append(item)
                model.appendRow(items)
            return model
        
        
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
        
        self.models[key] = load_data_to_model(model, df)
        self.proxy_models[key] = proxy_model
        
        table_view = QTableView()
        table_view.setModel(proxy_model)
        
        self.chart_canvas = QLabel("Graphiques")
        
        self.update_statistics(key, df)
        self.update_table(key, df)
        
        # Gestion filtre et header
        header = FilterHeaderView(table_view)
        header.set_filter_callback(apply_filter)
        header.create_filter_widgets(len(df.columns))
        table_view.setHorizontalHeader(header)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        splitter = QHBoxLayout()
        splitter.addWidget(stats_table_widget)
        splitter.addWidget(self.chart_canvas)

        layou_split = QVBoxLayout()
        layou_split.addLayout(splitter)
        layou_split.addWidget(table_view)
        
        widget = QWidget()
        widget.setLayout(layou_split)
        
        self.tabs.addTab(widget, key)

    def update_table(self, key, df):
        
        df["Prix horaire (€)"] =  round(pd.to_numeric(df["Prix (€)"] / (df["Heures"] + df["Minutes"] / 60)).fillna(0).astype(float), 2)
        df["Prix au km (km)"] =   round(pd.to_numeric(df["Prix (€)"] / df["Distance (km)"]).fillna(0).astype(float), 2)
        df["CO2 par km (g/km)"] = round(pd.to_numeric(df["CO2 (kg)"] / df["Distance (km)"]*1000).fillna(0).astype(float), 2)
        
        model = self.models[key]
        model.clear()
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(df.columns)

        for row in df.itertuples(index=False):
            items = [QStandardItem(str(cell)) for cell in row]
            model.appendRow(items)

        self.proxy_models[key].invalidateFilter()

    def update_statistics(self, key, df):       
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
        
        pixmap = StatsWidget.update_stats(df, key)
        self.chart_canvas.setPixmap(pixmap)

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