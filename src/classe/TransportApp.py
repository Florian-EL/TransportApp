import pandas as pd
import sys
import os
import json
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QScrollArea, QWidget, \
    QGraphicsView, QGraphicsScene, QTableView, QTableWidget, QHeaderView, QTableWidgetItem, QSizePolicy, \
    QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from src.classe.DataManager import DataManager
from src.classe.Graph import update_stats, graph_stats
from src.classe.StatsWidget import StatsWidget
from src.classe.FilterHeaderView import FilterHeaderView, DateSortFilterProxyModel
from src.classe.Dialog import AddDataDialog, DelDataDialog


class TransportApp(QWidget):
    def __init__(self):
        super().__init__()
        
        try :
            with open(os.path.join(os.path.dirname(sys.executable), "src/assets/file.json"), "r", encoding="utf-8") as f:
                resources = json.load(f)
        except :
            with open("src/assets/file.json", "r", encoding="utf-8") as f:
                resources = json.load(f)
        
        noms = ["Train", "Métro", "Bus", "Fiesta", "Avion", "Taxi", "Marche"]
        aux_noms = ["Train_R", "Métro_Bus_R", "Fiesta_R", "Taxi_R"]
        paths = resources["data_files"]
        aux_paths = resources['aux_files']
        self.file_paths = {nom: Path(p) for nom, p in zip(noms, paths)}
        self.aux_paths = {nom: Path(p) for nom,p in zip(aux_noms, aux_paths)}
        
        self.dm = DataManager(self.file_paths, self.aux_paths)
        self.data = self.dm.data
        
        self.fixed_column_config = {
            'Train': {
                'visible': ["Départ", "Arrivée", "Train", "Société", "Classe", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Prix appliqué (€)", "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Métro': {
                'visible': ["Départ", "Arrivée", "Société", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Prix appliqué (€)", 'ID', "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Bus': {
                'visible': ["Départ", "Arrivée", "Société", "Energie", "Date", "Heures", "Minutes", "Distance (km)", "CO2 (kg)", "Prix appliqué (€)", 'ID', "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
                'rename': {"Prix appliqué (€)": "Prix (€)", "Prix horaire (€)" : "Prix horaire\n(€)", "Prix au km (km)" : "Prix au km\n(km)", "CO2 par km (g/km)" : "CO2 par km\n(g/km)"}
            },
            'Fiesta': {
                'visible': ["Essence", "Date", "Kilométrage (km)", "Quantité (L)", "Prix (€)", "Distance (km)", "Litre par 100km", "Prix au litre", "km journalier moy", " Heures", "Minutes", "CO2 (lg)", "Prix horaire (€)", "Prix au km (km)", "CO2 par km (g/km)"],
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
                'visible': ["Numéro semaine", "Année", "Date", "Pas par jour", "Distance par jour (km / jour)", "Calorie par jour", "Pas par semaine", "Distance (km)", "Calories", "Heures", "Minutes", "Pas par kilomètre", "Distance par trajet", "Taille de pas"],
                'rename': {"Distance par jour (km / jour)" : "Distance par jour\n(km / jour)"}
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
        self.models = {}
        self.proxy_models = {}
        self.stats_tables = {}
        self.scene = {}
        self.view = {}
        self.init_ui()

    def init_ui(self):
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
            self.dm.apply_transformations(key)
            df = self.dm.get(key) if key in self.dm.data else pd.DataFrame()
            aux_keys = key + "_R" if key + "_R" in self.dm.aux.keys() else None
            
            if "Métro" in key or "Bus" in key :
                aux_keys = "Métro_Bus_R"
            self._create_mode_tab(key, df, aux_keys)
        
        self._create_stats_tab()
        self.setLayout(self.layout)

    def _create_mode_tab(self, key, df: pd.DataFrame, aux_key=None):
        def apply_filter(col, text, target_proxy= None):
            proxy = target_proxy or proxy_model
            proxy.setFilterKeyColumn(col)
            proxy.setFilterRegularExpression(text)
        
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
        
        def compute_table_width(view: QTableView):
            total = view.verticalHeader().width()
            for c in range(view.model().columnCount()):
                total += view.columnWidth(c)
            return total + view.columnWidth(c)//3
        
        stats_table_widget = QTableWidget()
        stats_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stats_tables[key] = stats_table_widget
        
        df_to_load = df.copy()
        cfg = self.fixed_column_config.get(key) or self.fixed_column_config.get(key + '')
        if cfg:
            cols = [c for c in cfg['visible'] if c in df_to_load.columns]
            if cols:
                df_to_load = df_to_load[cols].copy()
                if cfg.get('rename'):
                    df_to_load.rename(columns=cfg.get('rename', {}), inplace=True)
        
        model = QStandardItemModel()
        date_col = df_to_load.columns.get_loc('Date')
        proxy_model = DateSortFilterProxyModel(self, date_column=date_col, key=key)
        proxy_model.setSourceModel(model)
        proxy_model.setSortRole(Qt.DisplayRole)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(-1)
        proxy_model.setDynamicSortFilter(True)
        
        self.models[key] = load_data_to_model(model, df_to_load)
        self.proxy_models[key] = proxy_model
        
        table_view = QTableView()
        table_view.setModel(proxy_model)
        table_view.setSortingEnabled(True)
        
        
        header = FilterHeaderView(table_view)
        header.set_filter_callback(apply_filter)
        header.create_filter_widgets(len(self.fixed_column_config[key]['visible']))
        header.sectionClicked.connect(lambda index: header.handle_header_click(index, proxy_model))
        header.setFixedHeight(100)
        table_view.setHorizontalHeader(header)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
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
        
        split_layout = QHBoxLayout()
        split_layout.addWidget(stats_table_widget)
        split_layout.addWidget(self.view[key])
        
        add_btn = QPushButton("Ajouter des données")
        del_btn = QPushButton("Supprimer des données")
        add_btn.setObjectName("addButton")
        del_btn.setObjectName("delButton")
        add_btn.clicked.connect(self.add_window)
        del_btn.clicked.connect(self.del_window)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        
        table_princ = QVBoxLayout()
        table_princ.addWidget(table_view)
        table_princ.addLayout(btn_layout)
        
        table_princ_w = QWidget()
        table_princ_w.setLayout(table_princ)
        table_princ_w.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        if aux_key :
            aux_df = self.dm.get_R(aux_key)
            
            aux_model = QStandardItemModel()                
            aux_date_col = aux_df.columns.get_loc('Date')                
            aux_proxy = DateSortFilterProxyModel(self, date_column=aux_date_col, key=aux_key)
            aux_proxy.setSourceModel(aux_model)
            aux_proxy.setSortRole(Qt.DisplayRole)
            aux_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
            aux_proxy.setFilterKeyColumn(-1)
            aux_proxy.setDynamicSortFilter(True)
            
            aux_to_load = aux_df.copy()
            aux_cfg = self.fixed_column_config.get(aux_key) or self.fixed_column_config.get(aux_key + '')
            if aux_cfg:
                acols = [c for c in aux_cfg.get('visible', []) if c in aux_to_load.columns]
                if acols:
                    aux_to_load = aux_to_load[acols].copy()
                    if aux_cfg.get('rename'):
                        aux_to_load.rename(columns=aux_cfg.get('rename', {}), inplace=True)
            
            self.models[aux_key] = load_data_to_model(aux_model, aux_to_load)
            self.proxy_models[aux_key] = aux_proxy
            
            aux_table_view = QTableView()
            aux_table_view.setModel(aux_proxy)
            aux_table_view.setSortingEnabled(True)
            aux_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            header_aux = FilterHeaderView(aux_table_view)
            header_aux.set_filter_callback(apply_filter)
            header_aux.create_filter_widgets(len(aux_to_load.columns))
            header_aux.sectionClicked.connect(lambda index: header_aux.handle_header_click(index, aux_proxy))
            aux_table_view.setHorizontalHeader(header_aux)
            
            aux_add = QPushButton(f"Ajouter autres données")
            aux_del = QPushButton(f"Supprimer autres données")
            aux_add.clicked.connect(lambda _checked, akey=aux_key, adf=aux_to_load: AddDataDialog(akey, {akey: adf}, parent=self).exec_())
            aux_del.clicked.connect(lambda _checked, akey=aux_key, adf=aux_to_load: DelDataDialog(akey, adf, parent=self).exec_())
            aux_v = QVBoxLayout()
            aux_v.addWidget(aux_table_view)
            aux_v.addWidget(aux_add)
            aux_v.addWidget(aux_del)
            
            aux_widget = QWidget()
            aux_widget.setLayout(aux_v)
            
            w_aux = compute_table_width(aux_table_view)
            aux_widget.setFixedWidth(w_aux)
            aux_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)            
            aux_table_view.sortByColumn(aux_df.columns.get_loc('Date'), Qt.DescendingOrder)
            
        else :
            aux_widget = QWidget()
        
        right_v = QHBoxLayout()
        right_v.addWidget(table_princ_w)
        right_v.addWidget(aux_widget)
        
        main_v = QVBoxLayout()
        main_v.addLayout(split_layout)
        main_v.addLayout(right_v)
        
        widget = QWidget()
        widget.setLayout(main_v)
        self.tabs.addTab(widget, key)
        
        table_view.sortByColumn(df_to_load.columns.get_loc('Date'), Qt.DescendingOrder)
        
    def _create_stats_tab(self):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Statistiques":
                self.tabs.removeTab(i)
                break
        
        columns = [
            'Année', 'Distance (km)', 'Prix (€)', 'Prix horaire (€)', 'Prix au km (km)',
            'parcours %', 'CO2 (kg)', 'CO2 par km (g/km)', 'CO2 par heures (kg/h)',
            'Equivalent jours', 'Equivalent vitesse (km/h)', 'Heures', 'Minutes',
        ]
        
        all_data = self.dm.concat_all()
        
        if all_data.empty:
            widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Aucune donnée disponible"))
            widget.setLayout(layout)
            self.tabs.insertTab(0, widget, "Statistiques")
            return
        
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
        
        for i, row in stats.iterrows():
            for j, col in enumerate(columns):
                value = row[col]
                if col == "Année":
                    value = int(value)
                stats_table_widget.setItem(i, j, QTableWidgetItem(str(value)))
        stats_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # Ajuster la hauteur en fonction du nombre de lignes (header + lignes)
        try:
            stats_table_widget.resizeRowsToContents()
            header_h = stats_table_widget.horizontalHeader().height()
            rows_h = sum(stats_table_widget.rowHeight(r) for r in range(stats_table_widget.rowCount()))
            total_h = header_h + rows_h + 12
            # limiter une hauteur raisonnable
            max_h = 800
            stats_table_widget.setFixedHeight(min(total_h, max_h))
        except Exception:
            pass
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Statistiques générales"))
        layout.addWidget(stats_table_widget)
        
        
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
                df_mode = self.dm.data[mode]
                df_annee_mode = df_mode[df_mode['Année'] == annee] if not df_mode.empty and 'Année' in df_mode.columns else pd.DataFrame()
                if not df_annee_mode.empty or True:
                    # valeurs issues des données principales
                    distance = round(df_annee_mode['Distance (km)'].sum(), 2) if ('Distance (km)' in df_annee_mode.columns and not df_annee_mode.empty) else 0
                    heures = int(df_annee_mode['Heures'].sum() + df_annee_mode['Minutes'].sum() // 60) if ('Heures' in df_annee_mode.columns and 'Minutes' in df_annee_mode.columns and not df_annee_mode.empty) else 0
                    minutes = int(df_annee_mode['Minutes'].sum() % 60) if ('Minutes' in df_annee_mode.columns and not df_annee_mode.empty) else 0
                    prix_main = float(df_annee_mode['Prix (€)'].sum()) if ('Prix (€)' in df_annee_mode.columns and not df_annee_mode.empty) else 0.0
                    
                    # additionner les prix des annexes liées à ce mode
                    prix_aux = 0.0
                    for aux_key in self.dm.aux.keys():
                        if mode in aux_key:
                            aux_df = self.dm.data.get(aux_key, pd.DataFrame())
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
                    #print(d['Distance (km)'],stats[stats['Année'] == annee]['Distance (km)'].sum())
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
    
    def update_table(self, key, df):
        model = self.models[key]
        model.clear()
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
    
    def update_stats_table(self, key, df):
        stats_table_widget = self.stats_tables[key]
        stats_table_widget.clearContents()
        stats_table_widget.setRowCount(0)
        stats_table_widget = StatsWidget.update_statistics(self, key, df)
        stats_table_widget.resizeRowsToContents()
        self.scene[key].clear()
        try:
            pixmap = update_stats(df)
            self.scene[key].addPixmap(pixmap)
            self.scene[key].setSceneRect(QRectF(pixmap.rect()))
            self.view[key].setFixedSize(pixmap.width(), pixmap.height())
        except Exception:
            pass
        self.view[key].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data[key] = df.copy(deep=True)
        current_tab_text = None
        try:
            current_tab_text = self.tabs.tabText(self.tabs.currentIndex())
        except Exception:
            current_tab_text = None
        stats_index = None
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Statistiques":
                stats_index = i
                break
        if stats_index is not None:
            self.tabs.removeTab(stats_index)
        self._create_stats_tab()
        if current_tab_text:
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == current_tab_text:
                    self.tabs.setCurrentIndex(i)
                    break
    
    def update_stats_tab(self, key, df):
        model = self.models[key]
        model.clear()
        df = df.reset_index(drop=True)
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels(df.columns)
        for row in df.itertuples(index=False):
            items = []
            for cell in row:
                item = QStandardItem(str(cell))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignTop)
                items.append(item)
            model.appendRow(items)
        self.proxy_models[key].invalidateFilter()
    
    def add_window(self):
        key = self.tabs.tabText(self.tabs.currentIndex())
        if key in self.dm.data:
            df = self.dm.get(key)
            header_cols = list(pd.read_csv(str(self.dm.file_paths[key]), sep=';', nrows=0).columns)
            
            useful_cols = [c for c in header_cols if c in df.columns]
            if not useful_cols:
                useful_cols = list(df.columns)
            donneebrut = {key: df[useful_cols].copy(deep=True)}
            dlg = AddDataDialog(key, donneebrut, parent=self)
            dlg.exec_()
    
    def del_window(self):
        key = self.tabs.tabText(self.tabs.currentIndex())
        if key in self.dm.data:
            df = self.dm.get(key)
            try:
                header_cols = list(pd.read_csv(str(self.dm.file_paths[key]), sep=';', nrows=0).columns)
            except Exception:
                header_cols = list(df.columns)
            
            useful_cols = [c for c in header_cols if c in df.columns]
            
            if not useful_cols:
                useful_cols = list(df.columns)

            donneebrut = {key: df.copy(deep=True)}
            dlg = DelDataDialog(key, donneebrut, parent=self)
            dlg.exec_()
