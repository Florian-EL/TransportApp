import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import pandas as pd
from matplotlib.ticker import FuncFormatter
from PyQt5.QtGui import QPixmap, QImage

def update_stats(data):
    fig, ax1 = plt.subplots(figsize=(3, 2), facecolor='black') #largeur x hauteur
    
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
    ax1.tick_params(colors='white')
    ax1.set_ylabel("Valeurs", color='white')
    ax1.set_xlabel("Année", color='white')
    
    # Axe 2
    ax2 = ax1.twinx()
    # Heures
    ax2.bar(x, grouped['Heures_tot'], width=width, label='Heures', color='tab:orange')
    # Trajets
    ax2.bar(x + width, grouped['count'], width=width, label='Trajets', color='tab:green')
    # CO2
    ax2.bar(x + width*2, grouped['CO2 (kg)'], width=width, label='CO2', color='tab:cyan')
    ax2.tick_params(colors='white')
    ax2.set_ylabel("Valeurs", color='white')
    
    plt.xticks(x, color='white')
    plt.yticks(color='white')

    ax1.set_facecolor('black')
    fig.patch.set_facecolor('black')
    
    ax1.set_yscale('log')
    formatter = FuncFormatter(lambda x, _: f'{int(x)}')
    ax1.yaxis.set_major_formatter(formatter)
    ax1.tick_params(axis='y', colors='white')
    ax1.yaxis.label.set_color('white')
    for label in ax1.get_yticklabels():
        label.set_color('white')

    ax1.tick_params(axis='x', colors='white')
    ax1.xaxis.label.set_color('white')
    for label in ax1.get_xticklabels():
        label.set_color('white')
    
    ax1.grid(True, which='both', axis='both', color='white', linestyle='--', linewidth=0.5, alpha=0.3)
    ax2.grid(False)
    
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.2, 0.9))
    
    plt.xticks(x)
    
    # Fond noir pour les axes aussi
    ax1.set_facecolor('black')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='black')
    plt.close()
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    
    return QPixmap.fromImage(qimage)


def graph_stats(data):
    fig, ax = plt.subplots(figsize=(3, 2), facecolor='black') #largeur x hauteur
    
    data = pd.DataFrame(data.copy())
    
    transport_order = ["Train", "Metro", "Bus", "Fiesta", "Marche", "Avion", "Taxi"]

    # Regrouper et réindexer selon l'ordre
    grouped = data.groupby('Transport')['Distance (km)'].sum()
    grouped = grouped.reindex(transport_order).dropna()
    labels = grouped.index
    sizes = grouped.values
    
    legend_labels = [f"{label} : {round(float(km), 2)} km / {round(float(km)/sizes.sum()*100, 2)} %" for label, km in zip(labels, sizes)]
    
    wedges, _ = ax.pie(
        sizes, labels=None, autopct=None, startangle=90, textprops={'color':"w"}
    )
    
    ax.legend(wedges, legend_labels, title="Transport", loc='center left', bbox_to_anchor=(1, 0.5))
    
    ax.axis('equal')  # Camembert circulaire
    
    # Fond noir pour les axes aussi
    ax.set_facecolor('black')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='black')
    plt.close()
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    
    return QPixmap.fromImage(qimage)