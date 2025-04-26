import sys
from PyQt5.QtWidgets import (QApplication)
from PyQt5.QtGui import QIcon

from src.classe.TransportApp import TransportApp

import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransportApp()
    window.setWindowIcon(QIcon("src/assets/app_icon.ico"))
    window.showMaximized()
    window.show()
    sys.exit(app.exec_())
