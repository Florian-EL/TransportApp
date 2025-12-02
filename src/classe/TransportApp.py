import pandas as pd
import sys
import os
import json
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QScrollArea, QWidget as QW, \
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
    def __init__(self, config_path="src/assets/file.json"):
        super().__init__()
        #os.path.join(os.path.dirname(sys.executable),
        with open(os.path.join(config_path), "r", encoding="utf-8") as f:
            resources = json.load(f)
        noms = ["Train", "Métro", "Bus", "Fiesta", "Avion", "Taxi", "Marche"]
        paths = resources["data_files"]
        self.file_paths = {nom: Path(p) for nom, p in zip(noms, paths)}
        
        self.dm = DataManager(self.file_paths)
        self.data = self.dm.data
        self.models = {}
        self.proxy_models = {}
        self.stats_tables = {}
        self.scene = {}
        self.view = {}
        self.init_ui()

    def init_ui(self):
        #os.path.join(os.path.dirname(sys.executable), 
        with open(os.path.join("src/assets/style.css"), "r") as f:
            self.setStyleSheet(f.read())
        self.setWindowTitle("Transport App")
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # créer onglets par mode
        for key in self.dm.data.keys():
            # appliquer transformations persistantes
            self.dm.apply_transformations(key)
            df = self.dm.get(key)
            self._create_mode_tab(key, df)

        # onglet stat global
        self._create_stats_tab()

        self.setLayout(self.layout)

    def _create_mode_tab(self, key, df: pd.DataFrame):
        # Stat widget (QTableWidget) + graphique miniature + table complète filtrable
        def apply_filter(col, text):
            proxy_model.setFilterKeyColumn(col)
            proxy_model.setFilterRegularExpression(text)
        
        # charger données dans model
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
        
        # table de stats mini
        stats_table_widget = QTableWidget()
        stats_table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.stats_tables[key] = stats_table_widget

        # modèle principal
        model = QStandardItemModel()
        # localement garder model avant d'y charger les données
        proxy_model = DateSortFilterProxyModel(self, date_column=df.columns.get_loc('Date'), key=key)
        proxy_model.setSourceModel(model)
        proxy_model.setSortRole(Qt.DisplayRole)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(-1)
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
        

        # layout
        split_layout = QHBoxLayout()
        split_layout.addWidget(stats_table_widget)
        split_layout.addWidget(self.view[key])

        main_v = QVBoxLayout()
        main_v.addLayout(split_layout)
        main_v.addWidget(table_view)

        # boutons add/del
        add_btn = QPushButton("Ajouter des données")
        del_btn = QPushButton("Supprimer les données")
        add_btn.setObjectName("addButton")
        del_btn.setObjectName("delButton")
        add_btn.clicked.connect(self.add_window)
        del_btn.clicked.connect(self.del_window)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        main_v.addLayout(btn_layout)

        widget = QWidget()
        widget.setLayout(main_v)
        self.tabs.addTab(widget, key)

        # trier par date si possible
        if 'Date' in df.columns:
            table_view.sortByColumn(df.columns.get_loc('Date'), Qt.DescendingOrder)

    def _create_stats_tab(self):
        # Reconstruire l'onglet "Statistiques" global à partir des données DM
        # Supprimer si existe
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

        all_data['Année'] = all_data['Année'].astype(int)

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

        # Table générale
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

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Statistiques générales"))
        layout.addWidget(stats_table_widget)

        # Détails par année (table + camembert)
        all_data['Année'] = all_data['Année'].astype(int)
        annees = sorted(stats['Année'].unique(), reverse=True)

        detail_columns = [
            'Transport', 'Distance (km)', 'Prix (€)', 'Prix horaire (€)', 'Prix au km (km)',
            'parcours %', 'CO2 (kg)', 'CO2 par km (g/km)', 'CO2 par heures (kg/h)',
            'Equivalent jours', 'Equivalent vitesse (km/h)', 'Heures', 'Minutes',
        ]

        layout_mini = QVBoxLayout()
        for annee in annees:
            layout_mini.addWidget(QLabel(f"Détail {annee}"))
            detail_stats = []
            for mode, df_mode in self.dm.data.items():
                df_annee_mode = df_mode[df_mode['Année'] == annee] if not df_mode.empty and 'Année' in df_mode.columns else pd.DataFrame()
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
                    d['Prix horaire (€)'] = round(d['Prix (€)'] / total_heures, 2) if total_heures else 0
                    d['Prix au km (km)'] = round(d['Prix (€)'] / d['Distance (km)'], 2) if d['Distance (km)'] else 0
                    d['CO2 par km (g/km)'] = round(d['CO2 (kg)'] / d['Distance (km)'] * 1000, 2) if d['Distance (km)'] else 0
                    d['Equivalent jours'] = round((d['Heures'] + d['Minutes']/60) / 24, 2)
                    d['Equivalent vitesse (km/h)'] = round(d['Distance (km)'] / (d['Heures'] + d['Minutes']/60), 2) if (d['Heures'] + d['Minutes']/60) else 0
                    d['parcours %'] = round(d['Distance (km)'] / all_data[all_data['Année'] == annee]['Distance (km)'].sum() * 100, 2)
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
            detail_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            detail_table.resizeRowsToContents()

            pixmap = graph_stats(detail_stats)
            pix_scene = QGraphicsScene()
            pix_view = QGraphicsView(pix_scene)
            pix_scene.addPixmap(pixmap)
            pix_scene.setSceneRect(QRectF(pixmap.rect()))
            pix_view.setFixedSize(550, pixmap.height() + 10)
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
        """Met à jour le tableur de statistiques pour refléter les modifications dans le DataFrame."""
        stats_table_widget = self.stats_tables[key]
        stats_table_widget.clearContents()  # Efface les données existantes
        stats_table_widget.setRowCount(0)  # Réinitialise le nombre de lignes

        # Recalculer les statistiques
        stats_table_widget = StatsWidget.update_statistics(self, key, df)
        stats_table_widget.resizeRowsToContents()
        
        self.scene[key].clear()
        pixmap = update_stats(df)
        self.scene[key].addPixmap(pixmap)
        self.scene[key].setSceneRect(QRectF(pixmap.rect()))
        
        self.view[key].setFixedSize(pixmap.width(), pixmap.height())
        self.view[key].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        self._create_stats_tab()

        # Restaurer l'onglet courant si possible
        if current_tab_text:
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == current_tab_text:
                    self.tabs.setCurrentIndex(i)
                    break
    #? utile ???
    def update_stats_tab(self, key, df):
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

    def add_window(self):
        key = self.tabs.tabText(self.tabs.currentIndex())
        if key in self.dm.data:
            df = self.dm.get(key)
            # Récupère l'entête (colonnes) du fichier CSV d'origine via DataManager.file_paths
            try:
                header_cols = list(pd.read_csv(str(self.dm.file_paths[key]), sep=';', nrows=0).columns)
            except Exception:
                # fallback: utilise les colonnes présentes dans le DataFrame chargé
                header_cols = list(df.columns)
            # ne garder que les colonnes à la fois dans l'entête d'origine et dans le df actuel
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
            dlg = DelDataDialog(key, df[useful_cols].copy(deep=True), parent=self)
            dlg.exec_()
