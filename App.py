from PyQt6.QtWidgets import QApplication

import sys

from AppWindow import MainWindow

sys.argv.append("--disable-web-security")
app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()