from PyQt6.QtWidgets import QApplication

import sys
import fontawesome

from AppWindow import MainWindow

sys.argv.append("--disable-web-security")
app = QApplication(sys.argv)
app.setStyleSheet(open('qss/MetaTreeView.qss', 'r').read() 
				  + open('qss/Main.qss', 'r').read()) 
				  #+ open('qss/bootstrap/css/bootstrap.css', 'r').read())
window = MainWindow()
window.show()

app.exec()