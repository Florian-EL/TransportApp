from PyQt5.QtWidgets import (QLineEdit, QHeaderView)
from PyQt5.QtCore import Qt

class FilterHeaderView(QHeaderView):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setSectionsClickable(True)
        self.filters = {}

    def set_filter_callback(self, filter_callback):
        """Définit le callback pour appliquer le filtre."""
        self.filter_callback = filter_callback

    def create_filter(self, col):
        """Crée un QLineEdit pour filtrer une colonne spécifique."""
        if col not in self.filters:
            filter_input = QLineEdit(self.parent())
            filter_input.setPlaceholderText("🔍")
            filter_input.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
            filter_input.setStyleSheet("border: none; background: transparent; font-size: 12px;")
            filter_input.textChanged.connect(lambda text: self.filter_callback(col, text))
            self.setFixedHeight(60)  # Ajuste la hauteur de l'en-tête

            self.filters[col] = filter_input

    def resizeEvent(self, event):
        """Redéfinit la taille des champs de filtre en fonction de la taille des colonnes."""
        super().resizeEvent(event)
        for col, filter_input in self.filters.items():
            rect = self.sectionViewportPosition(col)
            filter_input.setGeometry(rect, self.height() // 2, self.sectionSize(col), self.height() // 2)

    def paintSection(self, painter, rect, logicalIndex):
        """Dessine le titre + la boîte de filtre dans l'en-tête."""
        super().paintSection(painter, rect, logicalIndex)

        if logicalIndex in self.filters:
            filter_input = self.filters[logicalIndex]
            filter_input.setGeometry(rect.x(), rect.y() + rect.height() // 2, rect.width(), rect.height() // 2)
            filter_input.setVisible(True)
        else:
            self.create_filter(logicalIndex)
