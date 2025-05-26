from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView


def apply_color_gradient(table_widget):
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
            if not item:
                continue
            try:
                val = float(item.text())
                ratio = (val - min_val) / span
                r = int(255 * (1 - ratio))
                g = int(255 * ratio)
                item.setBackground(QColor(r, g, 0))
            except ValueError:
                continue

class StatsWidget:
    def __init__(self):
        pass
    
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
        stats['Distance (km)'] = round(stats['Distance (km)'], 2)
        stats['Heures'] = stats['Heures'] + stats['Minutes'] // 60
        stats['Minutes'] = stats['Minutes'] % 60
        stats['Prix horaire (€)'] = round(stats['Prix (€)'] / (stats['Heures'] + stats['Minutes'] / 60), 2)
        stats['Prix au km (km)'] = round(stats['Prix (€)'] / stats['Distance (km)'], 2)
        stats['CO2 par km (g/km)'] = round(stats['CO2 (kg)'] / stats['Distance (km)'] * 1000, 2)
        stats['Prix (€)'] = round(stats['Prix (€)'], 2)

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
        
        apply_color_gradient(stats_table_widget)
        return stats_table_widget
