import pandas as pd
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QTableWidget,\
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
            "Marche" : "data/marche.csv",
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
        
        self.donneebrut = {key: df.copy(deep=True) for key, df in self.data.items()}

        for key in self.data.keys():
            if key == "Fiesta" :
                self.calculate_fiesta(self.data[key])
            if key == 'Marche' :
                self.calculate_marche(self.data[key])
                self.add_tab(key, self.data[key])
                continue
            self.convert_to_number(self.data[key])
            self.add_tab(key, self.data[key])

        self.new_window_button = QPushButton("Ajouter des données")
        #self.save_button = QPushButton("Sauvegarder les données")

        self.new_window_button.clicked.connect(self.open_new_window)
        #self.save_button.clicked.connect(self.save_to_file)

        button_layout.addWidget(self.new_window_button)
        #button_layout.addWidget(self.save_button)
        
        self.layout.addWidget(self.tabs)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)
    
    def calculate_fiesta(self, df) :
        v_moy = 35.0 #km/h
        nb_h_tot = 23280 #h
        temps_th_volant = 445 #h
        temps_vol_pourcent = 1.912 #%
        co2 = 0.105 #kg/km
        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
        df.sort_values(by='Date', ascending=False)
        df['Kilométrage (km)'].astype(float)

        df['Distance (km)'] = (df['Kilométrage (km)'] - df['Kilométrage (km)'].shift(-1)).shift(1)
        
        df['Litre par 100km'] =  round(pd.to_numeric(df['Quantité (L)'] / df['Distance (km)']*100).fillna(0).astype(float), 2)
        df['Prix au litre'] = round(pd.to_numeric(df['Prix (€)'] / df['Quantité (L)']).fillna(0).astype(float), 4)

        df['km journalier moy'] = (round(pd.to_numeric(df['Distance (km)'].shift(-1) / (pd.to_datetime(df['Date']) - pd.to_datetime(df['Date'].shift(-1))).dt.days), 2)).shift(1)
        
        df['Heures'] = (round(df['Distance (km)'].shift(-1) / v_moy, 2)).shift(1)
        df['Minutes'] = (round((df['Distance (km)'].shift(-1) % v_moy)*100/60, 2)).shift(1)
        df['CO2 (kg)'] = co2 * df['Distance (km)']
    
    def calculate_marche(self, df) :
        nb_pas_par_min = 100
        nb_trajet_quotidien = 4
        
        df['Pas par semaine'] = pd.to_numeric(df['Moyenne de pas par jour']*7).fillna(0).astype(int)
        df['Distance (km)'] = round(pd.to_numeric(df['Distance moyenne par jour (km / jour)']*7, errors='coerce').fillna(0).astype(float), 2)
        df['Calories'] = pd.to_numeric(df['Calorie moyenne par jour']*7, errors='coerce').fillna(0).astype(float)
        
        df['Heures'] = pd.to_numeric(df['Pas par semaine']/nb_pas_par_min//60, errors='coerce').fillna(0).astype(int)
        df['Minutes'] = pd.to_numeric(df['Pas par semaine']/nb_pas_par_min%60, errors='coerce').fillna(0).astype(int)
        
        df['Date'] = df['Année'].astype(str) + " - " + df['Numéro semaine'].astype(str).str.zfill(2)
        
        df['Nombre de pas par kilomètre'] = pd.to_numeric(df['Pas par semaine']/df['Distance (km)'], errors='coerce').fillna(0).astype(int)
        df['Distance par trajet'] = round(pd.to_numeric(df['Distance (km)']/nb_trajet_quotidien, errors='coerce').fillna(0).astype(float), 2)
        df['Taille de pas'] = round(pd.to_numeric(100000/df['Nombre de pas par kilomètre'], errors='coerce').fillna(0).astype(float), 2)
        
        df['CO2 (kg)'] = 0
        df["Prix (€)"] = 0
        df.sort_values(by='Date', ascending=False, inplace=True)
        
    
    def convert_to_number(self, df):
        df['Heures'] = pd.to_numeric(df['Heures'], errors='coerce').fillna(0).astype(int)
        df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce').fillna(0).astype(int)
        df['Distance (km)'] = pd.to_numeric(df['Distance (km)'], errors='coerce').fillna(0).astype(float)
        df['Prix (€)'] = round(pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0).astype(float), 2)
        df['CO2 (kg)'] = round(pd.to_numeric(df['CO2 (kg)'], errors='coerce').fillna(0).astype(float), 2)
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
        
        stats_table_widget = StatsWidget.update_statistics(self, key, df)
        pixmap = StatsWidget.update_stats(self, df)
        self.chart_canvas.setPixmap(pixmap)
        
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
        #self.show_message("Données sauvegardées avec succès.")

    def open_new_window(self):
        """Ouvre une fenêtre pour ajouter des données."""
        key = self.tabs.tabText(self.tabs.currentIndex())
        if key in self.data:
            self.new_window = AddDataDialog(key, self.data[key], self.donneebrut, self)
            self.new_window.exec_()

    def show_message(self, message):
        """Affiche un message temporaire."""
        msg = QLabel(message)
        msg.setStyleSheet("color: green;")
        self.layout.addWidget(msg)
        QApplication.processEvents()