from PyQt5.QtWidgets import QHeaderView, QLineEdit
from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel

class FilterHeaderView(QHeaderView):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setSectionsClickable(True)
        self.filter_widgets = {}
        self.filter_height = 20

    def set_filter_callback(self, callback):
        """Configure un callback pour appliquer les filtres."""
        self.filter_callback = callback

    def create_filter_widgets(self, column_count):
        """Crée une zone de filtre pour chaque colonne."""
        for col in range(column_count):
            filter_widget = QLineEdit(self.parent())
            filter_widget.setPlaceholderText("Filtre")
            filter_widget.textChanged.connect(lambda text, col=col: self.filter_callback(col, text))
            self.filter_widgets[col] = filter_widget

    def resizeEvent(self, event):
        """Redimensionne les zones de filtre pour correspondre aux colonnes."""
        super().resizeEvent(event)
        offset = self.parent().verticalHeader().width()  # Largeur de l'index (numéros de lignes)
        for col, widget in self.filter_widgets.items():
            rect = self.sectionViewportPosition(col) + offset
            widget.setGeometry(rect, self.height() - self.filter_height, self.sectionSize(col), self.filter_height)

    def sizeHint(self):
        """Augmente la hauteur du header pour inclure les filtres."""
        base_size = super().sizeHint()
        return QSize(base_size.width(), base_size.height() + self.filter_height*2)

    def handle_header_click(self, column, proxy_model):
        current = self.sortIndicatorSection()
        order = self.sortIndicatorOrder()

        if column == current:
            order = Qt.DescendingOrder if order == 1 else Qt.AscendingOrder
        else:
            order = Qt.AscendingOrder

        proxy_model.sort(column, order)
        self.setSortIndicator(column, order)


class DateSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None, date_column=0, key=''):
        super().__init__(parent)
        self.date_column = date_column  # index de la colonne date
        self.key = key
        
    def lessThan(self, left, right):
        if left.column() == self.date_column:
            left_data = left.data(Qt.DisplayRole)
            right_data = right.data(Qt.DisplayRole)
            try:
                if self.key != 'Marche' :
                    left_date = pd.to_datetime(left_data, format='%d/%m/%Y', errors='coerce')
                    right_date = pd.to_datetime(right_data, format='%d/%m/%Y', errors='coerce')
                else :
                    left_date = pd.to_datetime(left_data, format='%Y - %W', errors='coerce')
                    right_date = pd.to_datetime(right_data, format='%Y - %W', errors='coerce')
                return left_date < right_date
            except Exception :
                pass
        # Pour les autres colonnes, comportement par défaut (texte ou nombre)
        return super().lessThan(left, right)