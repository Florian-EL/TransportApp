import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage

class StatsWidget:
    @staticmethod
    def update_stats(data):
        # Génère une figure
        plt.figure(figsize=(2, 2))
        data_counts = {key: len(df) for key, df in data.items()}
        plt.bar(data_counts.keys(), data_counts.values(), color=['blue', 'green', 'red'])
        plt.xlabel("Types de Transport")
        plt.ylabel("Nombre d'entrées")
        plt.title("Répartition des données")

        # Sauvegarde dans un buffer mémoire
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        # Charge dans PIL
        img = Image.open(buf).convert("RGBA")

        # Convertit PIL.Image en QImage
        data = img.tobytes("raw", "RGBA")
        qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)

        # Retourne un QPixmap
        return QPixmap.fromImage(qimage)
