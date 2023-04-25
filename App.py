from PyQt6.QtWidgets import QApplication

import sys

from AppWindow import MainWindow

sys.argv.append("--disable-web-security")
app = QApplication(sys.argv)
app.setStyleSheet(open('qss/MetaTreeView.qss', 'r').read() 
				  + open('qss/JobStatus.qss', 'r').read() 
				  + open('qss/NavBar.qss', 'r').read() 
				  + open('qss/Main.qss', 'r').read()) 
				  #+ open('qss/bootstrap/css/bootstrap.css', 'r').read())
window = MainWindow()
window.show()

app.exec()