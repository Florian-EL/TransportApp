import pandas as pd
import json
import os
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QTableWidget, QGraphicsView,\
                            QGraphicsScene, QWidget, QPushButton, QTabWidget, QSizePolicy, QHeaderView,\
                            QTableView, QLabel, QTableWidgetItem, QScrollArea


from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from src.classe.FilterHeaderView import FilterHeaderView
from src.classe.AddDataDialog import AddDataDialog
from src.classe.DelDataDialog import DelDataDialog
from src.classe.StatsWidget import StatsWidget

from src.classe.Graph import update_stats, graph_stats

from src.classe.FilterHeaderView import DateSortFilterProxyModel


class TransportApp(QWidget):
    def __init__(self):
        super().__init__()
        #os.path.join(os.path.dirname(sys.executable), 
        with open("src/assets/file.json", "r", encoding="utf-8") as f:
            resources = json.load(f)
        
        self.file_paths = resources["data_files"]
        noms = ["Train", "Métro", "Bus", "Fiesta", "Avion", "Taxi", "Marche"]
        self.file_paths = {nom: chemin for nom, chemin in zip(noms, self.file_paths)}
        
        
        #self.file_paths = {
        #    "Train" : "data/train.csv",
        #    "Metro" : "data/metro.csv",
        #    "Bus" :   "data/bus.csv",
        #    "Fiesta" :"data/fiesta.csv",
        #    "Avion" : "data/avion.csv",
        #    "Taxi" :  "data/taxi.csv",
        #    "Marche" : "data/marche.csv",
        #}
        
        self.data = {key: self.load_data(path) for key, path in self.file_paths.items()}
        self.models = {}
        self.tables = {}
        self.stats_tables = {}
        self.proxy_models = {}
        self.filters = {}
        self.init_ui()

    def init_ui(self):
        #os.path.join(os.path.dirname(sys.executable), 
        with open("src/assets/style.css", "r") as f:
            self.setStyleSheet(f.read())
        self.setWindowTitle("Transport App")

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        
        self.scene = {}
        self.view = {}
        
        data = self.data.copy()
        
        for key in self.data.keys():
            if key == "Fiesta" :
                self.calculate_fiesta(data[key])
                self.convert_to_number(key, data[key])
            elif key == 'Marche' :
                self.calculate_marche(data[key])
            else :
                self.convert_to_number(key, data[key])
            self.add_tab(key, data[key])
        
        self.add_stats_tab()
        
        self.layout.addWidget(self.tabs)
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

        df['Quantité (L)'] = pd.to_numeric(df['Quantité (L)'], errors='coerce').fillna(0).astype(float)
        df['Prix (€)'] = pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0).astype(float)
        df['Kilométrage (km)'] = pd.to_numeric(df['Kilométrage (km)'], errors='coerce').fillna(0).astype(float)

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
        
        df['Pas par jour'] = pd.to_numeric(df['Pas par jour'], errors='coerce').fillna(0).astype(int)
        df['Calorie par jour'] = pd.to_numeric(df['Calorie par jour'], errors='coerce').fillna(0).astype(float)
        df['Distance par jour (km / jour)'] = pd.to_numeric(df['Distance par jour (km / jour)'], errors='coerce').fillna(0).astype(float)
        
        df['Pas par semaine'] = pd.to_numeric(df['Pas par jour']*7).fillna(0).astype(int)
        df['Distance (km)'] = round(pd.to_numeric(df['Distance par jour (km / jour)']*7, errors='coerce').fillna(0).astype(float), 2)
        df['Calories'] = pd.to_numeric(df['Calorie par jour']*7, errors='coerce').fillna(0).astype(float)
        
        df['Heures'] = pd.to_numeric(df['Pas par semaine']/nb_pas_par_min//60, errors='coerce').fillna(0).astype(int)
        df['Minutes'] = pd.to_numeric(df['Pas par semaine']/nb_pas_par_min%60, errors='coerce').fillna(0).astype(int)
        
        df['Date'] = df['Année'].astype(str) + " - " + df['Numéro semaine'].astype(str).str.zfill(2)
        df.sort_values(by='Date', ascending=False, inplace=True)
        
        df['Année'] = pd.to_numeric(df['Année'], errors='coerce').fillna(0).astype(int)
        
        df['Pas par kilomètre'] = pd.to_numeric(df['Pas par semaine']/df['Distance (km)'], errors='coerce').fillna(0).astype(int)
        df['Distance par trajet'] = round(pd.to_numeric(df['Distance (km)']/nb_trajet_quotidien, errors='coerce').fillna(0).astype(float), 2)
        df['Taille de pas'] = round(pd.to_numeric(100000/df['Pas par kilomètre'], errors='coerce').fillna(0).astype(float), 2)
        
        df['CO2 (kg)'] = 0
        df["Prix (€)"] = 0
        
    def convert_to_number(self, key, df):
        df['Heures'] = pd.to_numeric(df['Heures'], errors='coerce').fillna(0).astype(int)
        df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce').fillna(0).astype(int)
        df['Distance (km)'] = pd.to_numeric(df['Distance (km)'], errors='coerce').fillna(0).astype(float)
        df['Prix (€)'] = round(pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0).astype(float), 2)
        df['CO2 (kg)'] = round(pd.to_numeric(df['CO2 (kg)'], errors='coerce').fillna(0).astype(float), 2)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
        df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')        
        if key != 'Marche' :
            df['Année'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.year
            df["Prix horaire (€)"] =  round(pd.to_numeric(df["Prix (€)"] / (df["Heures"] + df["Minutes"] / 60)).fillna(0).astype(float), 2)
            df["Prix au km (km)"] =   round(pd.to_numeric(df["Prix (€)"] / df["Distance (km)"]).fillna(0).astype(float), 2)
            df["CO2 par km (g/km)"] = round(pd.to_numeric(df["CO2 (kg)"] / df["Distance (km)"]*1000).fillna(0).astype(float), 2)
        
        try :
            df['Classe'] = df["Classe"].astype(int)
        except Exception :
            pass

    def add_stats_tab(self):
        # Colonnes à afficher
        columns = [
            'Année', 'Distance (km)', 'Prix (€)', 'Prix horaire (€)', 'Prix au km (km)', \
            'parcours %', 'CO2 (kg)', 'CO2 par km (g/km)', 'CO2 par heures (kg/h)', \
            'Equivalent jours', 'Equivalent vitesse (km/h)',  'Heures', 'Minutes', 
        ]
        # Fusionner toutes les données dans un seul DataFrame
        all_data = pd.concat(self.data.values(), ignore_index=True)
        all_data['Année'] = all_data['Année'].astype(int)

        # Calcul des stats par année
        stats = all_data.groupby('Année').agg({
            'Distance (km)': 'sum',
            'Heures': 'sum',
            'Minutes': 'sum',
            'Prix (€)': 'sum',
            'CO2 (kg)': 'sum'
        }).reset_index()
        
        stats['Année'] = stats['Année'].astype(int)
        stats['Prix horaire (€)'] = round(stats['Prix (€)'] / (stats['Heures'] + stats['Minutes'] / 60), 2)
        stats['Prix au km (km)'] = round(stats['Prix (€)'] / stats['Distance (km)'], 2)
        stats['CO2 par km (g/km)'] = round(stats['CO2 (kg)'] / stats['Distance (km)'] * 1000, 2)
        stats['Distance (km)'] = round(stats['Distance (km)'], 2)
        stats['Prix (€)'] = round(stats['Prix (€)'], 2)
        stats['CO2 (kg)'] = round(stats['CO2 (kg)'], 2)
        stats['Heures'] = stats['Heures'] + stats['Minutes'] // 60
        stats['Minutes'] = stats['Minutes'] % 60
        stats['Equivalent jours'] = round((stats['Heures'] + stats['Minutes']/60) / 24, 2)
        stats['Equivalent vitesse (km/h)'] = round(stats['Distance (km)'] / (stats['Heures'] + stats['Minutes']/60), 2)
        stats['parcours %'] = round(stats['Distance (km)'] / stats['Distance (km)'].sum() * 100, 2)
        stats['CO2 par heures (kg/h)'] = round(stats['CO2 (kg)'] / (stats['Heures'] + stats['Minutes']/60), 2)
        
        # Créer la table unique
        stats_table_widget = QTableWidget()
        stats_table_widget.setColumnCount(len(columns))
        stats_table_widget.setRowCount(len(stats))
        stats_table_widget.setHorizontalHeaderLabels(columns)
        stats_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        for i, row in stats.iterrows():
            for j, col in enumerate(columns):
                value = row[col]
                if col == "Année" :
                    value = int(value)
                stats_table_widget.setItem(i, j, QTableWidgetItem(str(value)))
        stats_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        row_height = sum(stats_table_widget.rowHeight(i) for i in range(stats_table_widget.rowCount()))
        header_height = stats_table_widget.horizontalHeader().height()
        table_height = row_height + header_height + 12
        stats_table_widget.setMaximumHeight(table_height)
        
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Statistiques générales"))
        layout.addWidget(stats_table_widget)

        # Pour chaque année, ajouter un tableau détaillé par mode de transport
        all_data['Année'] = all_data['Année'].astype(int)
        annees = sorted(stats['Année'].unique(), reverse=True)

        detail_columns = [
            'Transport', 'Distance (km)', 'Prix (€)', 'Prix horaire (€)', 'Prix au km (km)', \
            'parcours %', 'CO2 (kg)', 'CO2 par km (g/km)', 'CO2 par heures (kg/h)', \
            'Equivalent jours', 'Equivalent vitesse (km/h)',  'Heures', 'Minutes', 
        ]

        layout_mini = QVBoxLayout()
        for annee in annees:
            
            layout_mini.addWidget(QLabel(f"Détail {annee}"))
            detail_stats = []
            for mode, df_mode in self.data.items():
                # On filtre les données du mode pour l'année courante
                df_annee_mode = df_mode[df_mode['Année'] == annee]
                if not df_annee_mode.empty:
                    d = {
                        'Transport': mode,
                        'Distance (km)': round(df_annee_mode['Distance (km)'].sum(), 2),
                        'Heures': int(df_annee_mode['Heures'].sum() + df_annee_mode['Minutes'].sum() // 60),
                        'Minutes': int(df_annee_mode['Minutes'].sum() % 60),
                        'Prix (€)': round(df_annee_mode['Prix (€)'].sum(), 2),
                        'CO2 (kg)': round(df_annee_mode['CO2 (kg)'].sum(), 2),
                    }
                    total_heures = d['Heures'] + d['Minutes'] / 60
                    d['Prix horaire (€)'] = round(d['Prix (€)'] / total_heures, 2)
                    d['Prix au km (km)'] = round(d['Prix (€)'] / d['Distance (km)'], 2)
                    d['CO2 par km (g/km)'] = round(d['CO2 (kg)'] / d['Distance (km)'] * 1000, 2)
                    d['Equivalent jours'] = round((d['Heures'] + d['Minutes']/60) / 24, 2)
                    d['Equivalent vitesse (km/h)'] = round(d['Distance (km)'] / (d['Heures'] + d['Minutes']/60), 2)
                    d['parcours %'] = round(d['Distance (km)'] / all_data[all_data['Année'] == annee]['Distance (km)'].sum() * 100, 2)
                    d['CO2 par heures (kg/h)'] = round(d['CO2 (kg)'] / (d['Heures'] + d['Minutes']/60), 2)
                    detail_stats.append(d)
            # Créer la table détaillée pour l'année
            detail_table = QTableWidget()
            detail_table.setColumnCount(len(detail_columns))
            detail_table.setRowCount(len(detail_stats))
            detail_table.setHorizontalHeaderLabels(detail_columns)
            detail_table.resizeRowsToContents()
            for i, row in enumerate(detail_stats):
                for j, col in enumerate(detail_columns):
                    item = QTableWidgetItem(str(row[col]))
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)  # Aligner en haut et à gauche
                    detail_table.setItem(i, j, item)
            detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            detail_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            
            # Ajuste la hauteur pour afficher toutes les lignes sans scroll interne
            row_height = sum(detail_table.rowHeight(i) for i in range(detail_table.rowCount()))
            header_height = detail_table.horizontalHeader().height()
            table_height = row_height + header_height + 12
            detail_table.setMinimumHeight(table_height)
            #detail_table.setMaximumHeight(table_height)
            detail_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            
            pixmap = graph_stats(detail_stats)
            
            pix_scene = QGraphicsScene()
            pix_view = QGraphicsView(pix_scene)
            
            pix_scene.addPixmap(pixmap)
            pix_scene.setSceneRect(QRectF(pixmap.rect()))
            
            pix_view.setFixedSize(550, pixmap.height()+10)
        
            pix_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            pix_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            laout = QHBoxLayout()
            laout.addWidget(detail_table)
            laout.addWidget(pix_view)
            
            layout_mini.addLayout(laout)
        
        # 1. Mettre layout_mini dans un widget
        mini_widget = QWidget()
        mini_widget.setLayout(layout_mini)
        
        # 2. Créer la scroll area pour layout_mini
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(mini_widget)
        
        # 3. Ajouter la partie statique (layout) et la scroll area dans le layout principal
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)      # partie statique (statistiques générales)
        main_layout.addWidget(scroll)      # partie scrollable (détails par année)
        
        widget = QWidget()
        widget.setLayout(main_layout)
        self.tabs.insertTab(0, widget, "Statistiques")
    
    def add_tab(self, key, df):
        def apply_filter(col, text):
            proxy_model.setFilterKeyColumn(col)
            proxy_model.setFilterRegularExpression(text)
        
        def load_data_to_model(model, df):
            model.setColumnCount(len(df.columns))
            model.setHorizontalHeaderLabels(df.columns)

            for row in df.itertuples(index=False):
                items = []
                for col, cell in enumerate(row):
                    if df.columns[col] == 'Date' and type(cell) is not str :
                        cell = cell.strftime('%d/%m/%Y')
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
        proxy_model = DateSortFilterProxyModel(self, date_column=df.columns.get_loc('Date'), key=key)
        proxy_model.setSourceModel(model)
        proxy_model.setSortRole(Qt.DisplayRole)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(-1)  # Appliquer à toutes les colonnes
        proxy_model.setDynamicSortFilter(True)
        
        
        self.models[key] = load_data_to_model(model, df)
        self.proxy_models[key] = proxy_model
        
        table_view = QTableView()
        table_view.setModel(proxy_model)
        table_view.setSortingEnabled(True)
        
        self.scene[key] = QGraphicsScene()
        self.view[key] = QGraphicsView(self.scene[key])
        
        stats_table_widget = StatsWidget.update_statistics(self, key, df)
        stats_table_widget.setObjectName("statsTable")
        pixmap = update_stats(df)
        self.scene[key].addPixmap(pixmap)
        self.scene[key].setSceneRect(QRectF(pixmap.rect()))

        self.view[key].setFixedSize(pixmap.width(), pixmap.height())
        self.view[key].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view[key].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Gestion filtre et header
        header = FilterHeaderView(table_view)
        header.set_filter_callback(apply_filter)
        header.create_filter_widgets(len(df.columns))
        header.sectionClicked.connect(lambda index: header.handle_header_click(index, proxy_model))
        table_view.setHorizontalHeader(header)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        
        self.splitter = QHBoxLayout()
        self.splitter.addWidget(stats_table_widget)
        self.splitter.addWidget(self.view[key])
        
        layou_split = QVBoxLayout()
        layou_split.addLayout(self.splitter)
        layou_split.addWidget(table_view)
        
        
        add_windows = QPushButton("Ajouter des données")
        del_windows = QPushButton("Supprimer les données")
        add_windows.setObjectName("addButton")
        del_windows.setObjectName("delButton")

        add_windows.clicked.connect(self.add_window)
        del_windows.clicked.connect(self.del_window)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_windows)
        button_layout.addWidget(del_windows)
        
        layout_bouton = QVBoxLayout()
        layout_bouton.addLayout(layou_split)
        layout_bouton.addLayout(button_layout)
        
        widget = QWidget()
        widget.setLayout(layout_bouton)
        
        self.tabs.addTab(widget, key)
        
        table_view.sortByColumn(df.columns.get_loc('Date'), Qt.DescendingOrder)


    def update_table(self, key, df):
        """Met à jour le tableau pour refléter les modifications dans le DataFrame."""
        model = self.models[key]
        model.clear()  # Efface les données existantes dans le modèle

        # Réinitialiser les indices du DataFrame
        df = df.reset_index(drop=True)

        # Recharger les données dans le modèle
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(df.columns)

        for row in df.itertuples(index=False):
            items = []
            for cell in row:
                item = QStandardItem(str(cell))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)  # Aligner le texte
                items.append(item)
            model.appendRow(items)
        self.proxy_models[key].invalidateFilter()

    def update_stats_table(self, key, df):
            
            # Met à jour les données internes puis reconstruit l'onglet "Statistiques"
            # On copie les données fournies dans self.data
            self.data[key] = df.copy(deep=True)

            # Sauvegarder l'onglet courant (par texte) pour tenter de le restaurer après reconstruction
            current_tab_text = None
            try:
                current_tab_text = self.tabs.tabText(self.tabs.currentIndex())
            except Exception:
                current_tab_text = None

            # Supprimer l'onglet Statistiques s'il existe
            stats_index = None
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "Statistiques":
                    stats_index = i
                    break
            if stats_index is not None:
                self.tabs.removeTab(stats_index)

            # Reconstruire l'onglet Statistiques en réutilisant add_stats_tab qui travaille sur self.data
            self.add_stats_tab()

            # Restaurer l'onglet courant si possible
            if current_tab_text:
                for i in range(self.tabs.count()):
                    if self.tabs.tabText(i) == current_tab_text:
                        self.tabs.setCurrentIndex(i)
                        break


    def update_stat_tab(self, key, df):
        """Met à jour le tableau pour refléter les modifications dans le DataFrame."""
        model = self.models[key]
        model.clear()  # Efface les données existantes dans le modèle

        # Réinitialiser les indices du DataFrame
        df = df.reset_index(drop=True)

        # Recharger les données dans le modèle
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(df.columns)

        for row in df.itertuples(index=False):
            items = []
            for cell in row:
                item = QStandardItem(str(cell))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)  # Aligner le texte
                items.append(item)
            model.appendRow(items)
        self.proxy_models[key].invalidateFilter()

    def load_data(self, file_path):
        """Charge les données depuis un fichier CSV."""
        try:
            return pd.read_csv(file_path, delimiter=";")
        except FileNotFoundError:
            return pd.DataFrame(columns=["Date", "Type", "Distance", "Heures", "Minutes", "Prix", "CO2"])

    def add_window(self):
        """Ouvre une fenêtre pour ajouter des données."""
        key = self.tabs.tabText(self.tabs.currentIndex())
        donneebrut = {key: df.copy(deep=True) for key, df in {key: self.load_data(path) for key, path in self.file_paths.items()}.items()}
        if key in self.data:
            self.new_window = AddDataDialog(key, donneebrut, self)
            self.new_window.exec_()
            
    def del_window(self):
        """Ouvre une fenêtre pour ajouter des données."""
        key = self.tabs.tabText(self.tabs.currentIndex())
        donneebrut = {key: df.copy(deep=True) for key, df in {key: self.load_data(path) for key, path in self.file_paths.items()}.items()}
        if key in self.data:
            self.new_window = DelDataDialog(key, donneebrut[key], self)
            self.new_window.exec_()

    def show_message(self, message):
        """Affiche un message temporaire."""
        msg = QLabel(message)
        msg.setStyleSheet("color: green;")
        self.layout.addWidget(msg)
        QApplication.processEvents()