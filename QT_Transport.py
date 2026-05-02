import pandas as pd
import sys
import os
import json
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QScrollArea, QWidget, \
    QGraphicsView, QGraphicsScene, QTableView, QTableWidget, QHeaderView, QTableWidgetItem, QSizePolicy, \
    QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor


from src.classe.DataManager import DataManager
from src.classe.Graph import update_stats, graph_stats, global_stats
from src.classe.FilterHeaderView import FilterHeaderView, DateSortFilterProxyModel
from src.classe.Dialog import AddDataDialog, DelDataDialog


class TransportApp(QWidget) :
    def __init__(self) :
        super().__init__()
        
        try :
            with open(os.path.join(os.path.dirname(sys.executable), "src/assets/file.json"), "r", encoding="utf-8") as f:
                resources = json.load(f)
        except :
            with open("src/assets/file.json", "r", encoding="utf-8") as f:
                resources = json.load(f)
        
        noms = ["Train", "Métro", "Bus", "Fiesta", "Avion", "Taxi", "Marche", "Vélo"]
        aux_noms = ["Train_R", "Métro_Bus_R", "Fiesta_R", "Taxi_R"]
        self.index = {"Train" : 1,
                    "Métro" : 2,
                    "Bus" : 3,
                    "Fiesta" : 4,
                    "Avion" : 5,
                    "Taxi" : 6,
                    "Marche" : 7,
                    "Vélo" : 8,
                    }
        
        self.fixed_column_config = {
            'Train': {
                'visible': ["Départ", "Arrivée", "Train", "Société", "Classe", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Prix appliqué (€)", "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Métro': {
                'visible': ["Départ", "Arrivée", "Société", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Prix appliqué (€)", 'Abonnement', 'ID', "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Bus': {
                'visible': ["Départ", "Arrivée", "Société", "Energie", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Prix appliqué (€)", 'Abonnement', 'ID', "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Fiesta': {
                'visible': ["Essence", "Date", "Kilométrage (km)", "Quantité (L)", "Prix (€)", "Distance (km)", "Litre par 100km", "Prix au litre", "km journalier moy", "Heures", "Minutes", "CO2 (kg)", "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Avion': {
                'visible': ["Départ", "Arrivée", "Société", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Prix appliqué (€)", "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Taxi': {
                'visible': ["Départ", "Arrivée", "Société", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Litre", "Prix appliqué (€)", "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Marche': {
                'visible': ["Numéro semaine", "Année", "Date", "Pas par jour", "Distance par jour (km / jour)", "Calorie par jour", "Pas par semaine", "Distance (km)", "Calories", "Heures", "Minutes", "Pas par kilomètre", "Distance par trajet", "Taille de pas", "CO2 (kg)", "Prix appliqué (€)"],
                'rename': {"Prix appliqué (€)": "Prix (€)"}
            },
            'Vélo': {
                'visible': ["Date", "Distance (km)", "Heures", "Minutes", "CO2 (kg)", "Prix appliqué (€)"],
                'rename': {"Prix appliqué (€)": "Prix (€)"}
            },
            'Train_R': {
                'visible': ["Opération", "Date", "Prix (€)", "Retard"],
                'rename': {}
            },
            'Métro_Bus_R': {
                'visible': ["Opération", "Date", "Prix (€)", "Abonnement", "ID"],
                'rename': {}
            },
            'Fiesta_R': {
                'visible': ["Opération", "Date", "Prix (€)"],
                'rename': {}
            },
            'Taxi_R': {
                'visible': ["Opération", "Date", "Prix (€)"],
                'rename': {}
            },
        }
        
        paths = resources["data_files"]
        aux_paths = resources['aux_files']
        
        self.file_paths = {nom: Path(p) for nom, p in zip(noms, paths)}
        self.aux_paths = {nom: Path(p) for nom,p in zip(aux_noms, aux_paths)}
        
        self.dm = DataManager(self.file_paths, self.aux_paths)
        
        self.models = {}
        self.proxy_models = {}
        self.stats_tables = {}
        self.scene = {}
        self.view = {}
        
        self.init_ui()
    
    def init_ui(self) :
        try :
            with open(os.path.join(os.path.dirname(sys.executable), "src/assets/style.css"), "r") as f:
                self.setStyleSheet(f.read())
        except :
            with open("src/assets/style.css", "r") as f:
                self.setStyleSheet(f.read())
        
        self.setWindowTitle("Transport App")
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        for key in list(self.file_paths.keys()):
            aux_keys = key + "_R" if key + "_R" in self.dm.aux.keys() else None
            aux_keys = "Métro_Bus_R" if "Métro" in key or "Bus" in key else aux_keys
            
            self.create_mode_tab(key, aux_keys)
        
        self.create_statistiques_tab()
        
        self.setLayout(self.layout)
    
    def create_statistiques_tab(self) :
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Statistiques":
                self.tabs.removeTab(i)
                break
        
        stats_table_layout = self.create_global_stat_table()
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Statistiques générales"))
        layout.addLayout(stats_table_layout)
        
        layout_mini = self.create_yearly_stat_table()
        
        mini_widget = QWidget()
        mini_widget.setLayout(layout_mini)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(mini_widget)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(scroll)
        
        widget = QWidget()
        widget.setLayout(main_layout)
        self.tabs.insertTab(0, widget, "Statistiques")
    
    def create_global_stat_table(self) :
        all_data = self.dm.concat_all()
        
        columns = [
        'Année', 'Distance\n(km)', 'Prix\n(€)', 'Prix horaire\n(€)', 'Prix au km\n(km)',
        'parcours\n%', 'CO2\n(kg)', 'CO2 par km\n(g/km)', 'CO2 par heures\n(kg/h)',
        'Equivalent jours', 'Equivalent vitesse\n(km/h)', 'Heures', 'Minutes',
        ]
        
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
        stats['CO2 (kg)'] = round(stats['CO2 (kg)'], 4)
        stats['Heures'] = stats['Heures'] + stats['Minutes'] // 60
        stats['Minutes'] = stats['Minutes'] % 60
        stats['Equivalent jours'] = round((stats['Heures'] + stats['Minutes']/60) / 24, 2)
        stats['Equivalent vitesse (km/h)'] = round(stats['Distance (km)'] / (stats['Heures'] + stats['Minutes']/60), 2)
        stats['parcours %'] = round(stats['Distance (km)'] / stats['Distance (km)'].sum() * 100, 2)
        stats['CO2 par heures (kg/h)'] = round(stats['CO2 (kg)'] / (stats['Heures'] + stats['Minutes']/60), 2)
        
        stats_table_widget = QTableWidget()
        stats_table_widget.setColumnCount(len(columns))
        stats_table_widget.setRowCount(len(stats))
        stats_table_widget.setHorizontalHeaderLabels(columns)
        stats_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        stats_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        for i, row in stats.iterrows():
            for j, col in enumerate(stats.columns):
                value = row[col]
                if col == "Année":
                    value = int(value)
                stats_table_widget.setItem(i, j, QTableWidgetItem(str(value)))
        
        stats_table_widget.resizeRowsToContents()
        header_h = stats_table_widget.horizontalHeader().height()
        rows_h = sum(stats_table_widget.rowHeight(r) for r in range(stats_table_widget.rowCount()))
        total_h = header_h*2 + rows_h + 12
        max_h = 800
        stats_table_widget.setFixedHeight(min(total_h, max_h))
        stats_table_widget.sortByColumn(stats.columns.get_loc('Année'), Qt.DescendingOrder)
        
        pixmap = global_stats(stats)
        pix_scene = QGraphicsScene()
        pix_view = QGraphicsView(pix_scene)
        pix_scene.addPixmap(pixmap)
        pix_scene.setSceneRect(QRectF(pixmap.rect()))
        pix_view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pix_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        pix_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout_mini = QHBoxLayout()
        layout_mini.addWidget(stats_table_widget)
        layout_mini.addWidget(pix_view)
        
        return layout_mini
    
    def create_yearly_stat_table(self) :
        all_data = self.dm.concat_all()
        
        stats = all_data.groupby('Année').agg({
            'Distance (km)': 'sum',
            'Heures': 'sum',
            'Minutes': 'sum',
            'Prix (€)': 'sum',
            'CO2 (kg)': 'sum'
        }).reset_index()
        
        annees = sorted(stats['Année'].unique(), reverse=True)
        
        detail_columns = [
            'Transport', 'Distance (km)', 'Prix (€)', 'Prix horaire (€)', 'Prix au km (km)',
            'parcours %', 'CO2 (kg)', 'CO2 par km (g/km)', 'CO2 par heures (kg/h)',
            'Jours', 'Vitesse (km/h)', 'Heures', 'Minutes',
        ]
        
        layout_mini = QVBoxLayout()
        for annee in annees:
            if annee == 0 : continue
            layout_mini.addWidget(QLabel(f"Détail {annee}"))
            detail_stats = []
            
            for mode in self.file_paths.keys():
                df_mode = self.dm.get(mode)
                df_annee_mode = df_mode[df_mode['Année'] == annee] if not df_mode.empty and 'Année' in df_mode.columns else pd.DataFrame()
                if not df_annee_mode.empty or True:
                    # valeurs issues des données principales
                    distance = round(df_annee_mode['Distance (km)'].sum(), 2) if ('Distance (km)' in df_annee_mode.columns and not df_annee_mode.empty) else 0
                    heures = int(df_annee_mode['Heures'].sum() + df_annee_mode['Minutes'].sum() // 60) if ('Heures' in df_annee_mode.columns and 'Minutes' in df_annee_mode.columns and not df_annee_mode.empty) else 0
                    minutes = int(df_annee_mode['Minutes'].sum() % 60) if ('Minutes' in df_annee_mode.columns and not df_annee_mode.empty) else 0
                    prix_main = float(df_annee_mode['Prix (€)'].sum()) if ('Prix (€)' in df_annee_mode.columns and not df_annee_mode.empty) else 0.0
                    
                    # additionner les prix des annexes liées à ce mode
                    prix_aux = 0.0
                    mode_r = mode + "_R" if mode not in ["Bus", "Métro"] else "Métro_Bus_R"
                    if mode_r in self.dm.aux.keys() :
                        aux_df = self.dm.get_R(mode_r)
                        if not aux_df.empty and 'Année' in aux_df.columns and 'Prix (€)' in aux_df.columns:
                            prix_aux += float(aux_df[aux_df['Année'] == annee]['Prix (€)'].sum())
                    
                    prix_total = round(prix_main + prix_aux, 2)
                    
                    d = {
                        'Transport': mode,
                        'Distance (km)': distance,
                        'Heures': heures,
                        'Minutes': minutes,
                        'Prix (€)': prix_total,
                        'CO2 (kg)': round(df_annee_mode['CO2 (kg)'].sum(), 2) if ('CO2 (kg)' in df_annee_mode.columns and not df_annee_mode.empty) else 0,
                    }
                    
                    total_heures = d['Heures'] + d['Minutes'] / 60
                    d['Prix horaire (€)'] = round(d['Prix (€)'] / total_heures, 2) if total_heures else 0
                    d['Prix au km (km)'] = round(d['Prix (€)'] / d['Distance (km)'], 2) if d['Distance (km)'] else 0
                    d['CO2 par km (g/km)'] = round(d['CO2 (kg)'] / d['Distance (km)'] * 1000, 2) if d['Distance (km)'] else 0
                    d['Jours'] = round((d['Heures'] + d['Minutes']/60) / 24, 2)
                    d['Vitesse (km/h)'] = round(d['Distance (km)'] / (d['Heures'] + d['Minutes']/60), 2) if (d['Heures'] + d['Minutes']/60) else 0
                    d['parcours %'] = round(d['Distance (km)'] / stats[stats['Année'] == annee]['Distance (km)'].sum() * 100, 2) if stats[stats['Année'] == annee]['Distance (km)'].sum() else 0
                    d['CO2 par heures (kg/h)'] = round(d['CO2 (kg)'] / (d['Heures'] + d['Minutes']/60), 2) if (d['Heures'] + d['Minutes']/60) else 0
                    detail_stats.append(d)
            
            detail_table = QTableWidget()
            detail_table.setColumnCount(len(detail_columns))
            detail_table.setRowCount(len(detail_stats))
            detail_table.setHorizontalHeaderLabels(detail_columns)
            for i, row in enumerate(detail_stats):
                for j, col in enumerate(detail_columns):
                    item = QTableWidgetItem(str(row.get(col, "")))
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)
                    detail_table.setItem(i, j, item)
            detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
            # Let the detail table expand to fill available vertical space on the left
            detail_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            detail_table.resizeRowsToContents()
            # set a small minimum height based on content but allow expansion
            header_h = detail_table.horizontalHeader().height()
            rows_h = sum(detail_table.rowHeight(r) for r in range(detail_table.rowCount()))
            min_h = header_h + rows_h + 12
            detail_table.setMinimumHeight(min_h)
            
            
            pixmap = graph_stats(detail_stats)
            pix_scene = QGraphicsScene()
            pix_view = QGraphicsView(pix_scene)
            pix_scene.addPixmap(pixmap)
            pix_scene.setSceneRect(QRectF(pixmap.rect()))
            pix_view.setFixedSize(600, pixmap.height() + 10)
            pix_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            pix_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            h = QHBoxLayout()
            h.addWidget(detail_table)
            h.addWidget(pix_view)
            layout_mini.addLayout(h)
        
        
        return layout_mini
    
    def create_mode_tab(self, key, aux_key=None) :
        self.create_stat_table(key)
        self.create_stats_pixmap(key)
        
        split_layout = QHBoxLayout()
        split_layout.addWidget(self.stats_tables[key])
        split_layout.addWidget(self.view[key])
        
        main_layout = self.create_table(key)
        if aux_key is not None :
            aux_layout = self.create_table(aux_key)
        else : 
            aux_layout = QVBoxLayout()
        
        right_v = QHBoxLayout()
        right_v.addLayout(main_layout)
        right_v.addLayout(aux_layout)
        
        main_v = QVBoxLayout()
        main_v.addLayout(split_layout)
        main_v.addLayout(right_v)
        
        widget = QWidget()
        widget.setLayout(main_v)
        
        self.tabs.insertTab(self.index[key], widget, key)
    
    def create_table(self, key) :
        def create_proxy_model(key, model, date_col):
            proxy_model = DateSortFilterProxyModel(date_column=date_col, key=key)
            proxy_model.setSourceModel(model)
            proxy_model.setSortRole(Qt.DisplayRole)
            proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
            proxy_model.setFilterKeyColumn(-1)
            proxy_model.setDynamicSortFilter(True)
            return proxy_model

        def load_data_to_model(m, dataframe):
            m.clear()
            m.setColumnCount(len(dataframe.columns))
            m.setHorizontalHeaderLabels(list(dataframe.columns))
            for row in dataframe.itertuples(index=False):
                items = []
                for col_idx, cell in enumerate(row):
                    if dataframe.columns[col_idx] == 'Date' and not isinstance(cell, str) and not pd.isna(cell):
                        try:
                            cell = pd.to_datetime(cell).strftime('%d/%m/%Y')
                        except Exception:
                            cell = str(cell)
                    item = QStandardItem(str(cell))
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)
                    items.append(item)
                m.appendRow(items)
            return m

        def apply_filter(col, text):
            self.proxy_models[key].setFilterKeyColumn(col)
            self.proxy_models[key].setFilterRegularExpression(text)
        
        def compute_table_width(view: QTableView):
            total = view.verticalHeader().width()
            for c in range(view.model().columnCount()):
                total += view.columnWidth(c)
            return total + view.columnWidth(c)//3
        
        if "_R" in key :
            df = self.dm.get_R(key)
        else : 
            df = self.dm.get(key)
        
        df = df[[c for c in self.fixed_column_config.get(key)['visible'] if c in df.columns]]
        df.rename(columns=self.fixed_column_config.get(key)['rename'], inplace=True)
        
        model = QStandardItemModel()
        date_col = df.columns.get_loc('Date')
        
        
        
        self.models[key] = load_data_to_model(model, df) #? mystère
        self.proxy_models[key] = create_proxy_model(key, model, date_col)
        
        table_view = QTableView()
        table_view.setModel(self.proxy_models[key])
        table_view.setSortingEnabled(True)
        header = FilterHeaderView(table_view)
        header.set_filter_callback(apply_filter)
        header.create_filter_widgets(len(df.columns))
        header.sectionClicked.connect(lambda index: header.handle_header_click(index, self.proxy_models[key]))
        header.setFixedHeight(100)
        table_view.setHorizontalHeader(header)
        
        if "_R" in key :
            w_aux = compute_table_width(table_view)
            table_view.setFixedWidth(w_aux)
            table_view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) 
        else :
            table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        table_view.sortByColumn(df.columns.get_loc('Date'), Qt.DescendingOrder)
        
        table_princ = QVBoxLayout()
        table_princ.addWidget(table_view)
        table_princ.addLayout(self.create_button(key))
        
        return table_princ
    
    def create_stat_table(self, key) :
        columns = ['Année', 'Distance (km)', 'Heures', 'Minutes', 'Prix (€)',
                   'CO2 (kg)', 'Prix horaire\n(€)', 'Prix au km\n(km)',
                   'CO2 par km\n(g/km)']
        
        stats = self.update_statistics(key)
        
        stats_table_widget = QTableWidget()
        stats_table_widget.setColumnCount(len(columns))
        stats_table_widget.setRowCount(len(stats))
        stats_table_widget.setHorizontalHeaderLabels(columns)
        stats_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        stats_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        for i, row in stats.iterrows():
            for j, col in enumerate(stats.columns):
                value = row[col]
                if col == "Année":
                    value = int(value)
                stats_table_widget.setItem(i, j, QTableWidgetItem(str(value)))

        stats_table_widget.resizeRowsToContents()
        header_h = stats_table_widget.horizontalHeader().height()
        rows_h = sum(stats_table_widget.rowHeight(r) for r in range(stats_table_widget.rowCount()))
        total_h = header_h*2 + rows_h + 12
        max_h = 300
        stats_table_widget.setFixedHeight(min(total_h, max_h))
        stats_table_widget.sortByColumn(stats.columns.get_loc('Année'), Qt.DescendingOrder)

        #TODO stats_table_widget = self.apply_color_gradient(stats_table_widget)
        self.stats_tables[key] = stats_table_widget

    def create_stats_pixmap(self, key) :
        self.scene[key] = QGraphicsScene()
        
        df = self.dm.get(key)
        
        pixmap = update_stats(df)
        self.scene[key].addPixmap(pixmap)
        self.scene[key].setSceneRect(QRectF(pixmap.rect()))
        
        self.view[key] = QGraphicsView(self.scene[key])
        self.view[key].setFixedSize(pixmap.width(), pixmap.height())
        self.view[key].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view[key].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def apply_color_gradient(self, table_widget):
        row_count = table_widget.rowCount()
        col_count = table_widget.columnCount()

        for col in range(col_count):
            # Extraire les valeurs numériques de la colonne
            values = []
            for row in range(row_count):
                item = table_widget.item(row, col)
                if item:
                    try:
                        val = float(item.text())
                        values.append(val)
                    except ValueError:
                        continue

            if not values:
                continue

            min_val = min(values)
            max_val = max(values)
            span = max_val - min_val if max_val != min_val else 1

            # Appliquer le gradient
            for row in range(row_count):
                item = table_widget.item(row, col)
                if not item or col in [0, 6, 7, 8]:
                    continue
                try:
                    val = float(item.text())
                    ratio = (val - min_val) / span
                    r = int(255 * (1 - ratio))
                    g = int(255 * ratio)
                    item.setBackground(QColor(r, g, 0))
                except ValueError:
                    continue
        
        return table_widget
    
    def update_statistics(self, key):       
        local = self.dm.get(key)
        
        if key != "Marche" :
            local['Année'] = pd.to_datetime(local['Date'], dayfirst=True, errors='coerce').dt.year
        
        if 'Prix appliqué (€)' in local.columns:
            local['Prix (€)'] = local['Prix appliqué (€)']
        
        # Calcul des statistiques : somme et moyenne
        stats = local.groupby('Année').agg({
            'Distance (km)': 'sum',
            'Heures': 'sum',
            'Minutes': 'sum',
            'Prix (€)': 'sum',
            'CO2 (kg)': 'sum'
        }).reset_index()
        
        #stats.columns = ['Année', 'Distance (km)', 'Heures', 'Minutes', 'Prix (€)', 'CO2 (kg)']
        stats['Distance (km)'] = round(stats['Distance (km)'], 2)
        stats['Heures'] = stats['Heures'] + stats['Minutes'] // 60
        stats['Minutes'] = stats['Minutes'] % 60
        stats['Prix horaire\n(€)'] = round(stats['Prix (€)'] / (stats['Heures'] + stats['Minutes'] / 60), 2)
        stats['Prix au km\n(km)'] = round(stats['Prix (€)'] / stats['Distance (km)'], 2)
        stats['CO2 par km\n(g/km)'] = round(stats['CO2 (kg)'] / stats['Distance (km)'] * 1000, 2)
        stats['Prix (€)'] = round(stats['Prix (€)'], 2)
        stats['CO2 (kg)'] = round(stats['CO2 (kg)'], 2)
        
        return stats

    def update_tab(self, key):
        self.update_table(key)
        if key.endswith('_R') :
            if key == "Métro_Bus_R" :
                self.tabs.removeTab(self.index["Métro"])
                self.tabs.removeTab(self.index["Bus"]-1)
                self.create_mode_tab("Métro", "Métro_Bus_R")
                self.create_mode_tab("Bus", "Métro_Bus_R")
            else :
                self.tabs.removeTab(self.index[key[:-2]])
                self.create_mode_tab(key[:-2], key)
        else :
            if key == "Métro" or key == "Bus" :
                self.tabs.removeTab(self.index["Métro"])
                self.tabs.removeTab(self.index["Bus"]-1)
                self.create_mode_tab("Métro", "Métro_Bus_R")
                self.create_mode_tab("Bus", "Métro_Bus_R")
            else :
                self.tabs.removeTab(self.index[key])
                self.create_mode_tab(key, key + "_R" if key + "_R" in self.dm.aux.keys() else None)
        
        self.tabs.setCurrentIndex(self.index[key if not key.endswith('_R') else key[:-2]])
        
        self.tabs.removeTab(0)
        self.create_statistiques_tab()
    
    def update_table(self, key):
        model = self.models[key]
        model.clear()
        if "_R" in key :
            df = self.dm.get_R(key)
        else :
            df = self.dm.get(key)
        
        df = df.reset_index(drop=True)
        
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(list(df.columns))
        for row in df.itertuples(index=False):
            items = []
            for cell in row:
                item = QStandardItem(str(cell))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)
                items.append(item)
            model.appendRow(items)
        self.models[key] = model
        self.proxy_models[key].invalidateFilter()
    
    def create_button(self, key) :
        add_btn = QPushButton("Ajouter des données")
        del_btn = QPushButton("Supprimer des données")
        add_btn.setObjectName("addButton")
        del_btn.setObjectName("delButton")
        add_btn.clicked.connect(lambda checked, k=key: self.add_window(k))
        del_btn.clicked.connect(lambda checked, k=key: self.del_window(k))
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        return btn_layout

    def add_window(self, key):
        if key.endswith('_R') :
            df = self.dm.get_R(key)
            header_cols = list(pd.read_csv(str(self.dm.aux_file_paths[key]), sep=';', nrows=0).columns)
        else :
            df = self.dm.get(key)
            header_cols = list(pd.read_csv(str(self.dm.file_paths[key]), sep=';', nrows=0).columns)
        
        useful_cols = [c for c in header_cols if c in df.columns]
        if not useful_cols:
            useful_cols = list(df.columns)
        donneebrut = df[useful_cols].copy(deep=True)
        
        dlg = AddDataDialog(key, donneebrut, parent=self)
        dlg.setFixedWidth(400)
        dlg.exec_()
        
        self.update_tab(key)
    
    def del_window(self, key):
        if key.endswith('_R') :
            df = self.dm.get_R(key)
            header_cols = list(pd.read_csv(str(self.dm.aux_file_paths[key]), sep=';', nrows=0).columns)
        else :
            df = self.dm.get(key)
            header_cols = list(pd.read_csv(str(self.dm.file_paths[key]), sep=';', nrows=0).columns)
            
        useful_cols = [c for c in header_cols if c in df.columns]
        
        if not useful_cols:
            useful_cols = list(df.columns)

        donneebrut = df.copy(deep=True)
        dlg = DelDataDialog(key, donneebrut, parent=self)
        dlg.setFixedWidth(400)
        dlg.exec_()
        
        self.update_tab(key)
