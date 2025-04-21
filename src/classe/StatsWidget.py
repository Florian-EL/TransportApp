import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage
from matplotlib.ticker import FuncFormatter

class StatsWidget:
    @staticmethod
    def update_stats(data):
        fig, ax1 = plt.subplots(figsize=(3, 2)) #largeur x hauteur
        
        data = data.copy()
        data['Heures_tot'] = data['Heures'] + data['Minutes'] / 60
        
        grouped = data.groupby('Année').agg({
            'Distance (km)': 'sum',
            'Heures_tot': 'sum',
            'Société': 'count',
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
        ax2.bar(x + width, grouped['Société'], width=width, label='Trajets', color='tab:green')
        # CO2
        ax2.bar(x + width*2, grouped['CO2 (kg)'], width=width, label='CO2', color='tab:cyan')
        
        formatter = FuncFormatter(lambda x, _: f'{x/1000:.0f}')
        ax1.yaxis.set_major_formatter(formatter)
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.01, 1))
        
        plt.xticks(x)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimage)
