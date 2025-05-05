import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from matplotlib.ticker import FuncFormatter


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
        
        return stats_table_widget
    
    @staticmethod
    def update_stats(self, data):
        fig, ax1 = plt.subplots(figsize=(3, 2)) #largeur x hauteur
        
        data = data.copy()
        data['Heures_tot'] = data['Heures'] + data['Minutes'] / 60
        
        data['count'] = 1
        
        grouped = data.groupby('Année').agg({
            'Distance (km)': 'sum',
            'Heures_tot': 'sum',
            'count': 'count',
            'Prix (€)': 'sum',
            'CO2 (kg)': 'sum'
        }).reset_index()
        
        x = grouped['Année']
        width = 0.15
        
        # Axe 1
        # Distance
        ax1.bar(x - width*2, grouped['Distance (km)'], width=width, label='Kilomètres', color='tab:blue')
        # Prix
        ax1.bar(x - width, grouped['Prix (€)'], width=width, label='Prix', color='tab:red')
        
        # Axe 2
        ax2 = ax1.twinx()
        # Heures
        ax2.bar(x, grouped['Heures_tot'], width=width, label='Heures', color='tab:orange')
        # Trajets
        ax2.bar(x + width, grouped['count'], width=width, label='Trajets', color='tab:green')
        # CO2
        ax2.bar(x + width*2, grouped['CO2 (kg)'], width=width, label='CO2', color='tab:cyan')
        
        ax1.set_yscale('log')
        formatter = FuncFormatter(lambda x, _: f'{int(x)}')
        ax1.yaxis.set_major_formatter(formatter)
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.15, 0.9))
        
        plt.xticks(x)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        
        return QPixmap.fromImage(qimage)
