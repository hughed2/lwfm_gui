import sys
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from d3graph import d3graph, vec2adjmat

from PyQt6 import QtCore, QtGui, QtWidgets

class GraphD3Widget(QWidget):
    name = "Trigger List"
    
    def __init__(self, parent):
        super().__init__(parent)

        self.createGraph()

        self.initUI()

    def createGraph(self):
           #Set source and target nodes
        source = ['node A','node F','node B','node B','node B','node A','node C','node Z']
        target = ['node F','node B','node J','node F','node F','node M','node M','node A']
        weight = [5.56, 0.5, 0.64, 0.23, 0.9, 3.28, 0.5, 0.45]

        # Create adjacency matrix
        adjmat = vec2adjmat(source, target, weight=weight)

        # target  node A  node B  node F  node J  node M  node C  node Z
        # source                                                        
        # node A    0.00     0.0    5.56    0.00    3.28     0.0     0.0
        # node B    0.00     0.0    1.13    0.64    0.00     0.0     0.0
        # node F    0.00     0.5    0.00    0.00    0.00     0.0     0.0
        # node J    0.00     0.0    0.00    0.00    0.00     0.0     0.0
        # node M    0.00     0.0    0.00    0.00    0.00     0.0     0.0
        # node C    0.00     0.0    0.00    0.00    0.50     0.0     0.0
        # node Z    0.45     0.0    0.00    0.00    0.00     0.0     0.0

        # Initialize
        d3 = d3graph()

        adjmat, _ = d3.import_example('bigbang')

        # Build force-directed graph with default settings
        d3.graph(adjmat)
        d3.show(filepath='./graph_example.html')

    def initUI(self):

        _translate = QtCore.QCoreApplication.translate
        font = QtGui.QFont()
        font.setFamily("Helvetica Neue")


        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)

        self.header = QtWidgets.QLabel()
        self.header.setProperty("class", "header")
        self.header.setGeometry(QtCore.QRect(-2, 10, 751, 54))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setFont(font)
        self.header.setText(_translate("MainWindow", "Graph"))

        layout.addWidget(self.header)

        self.webEngineView = QWebEngineView()
        self.loadPage()

        layout.addWidget(self.webEngineView)

        self.footer = QtWidgets.QFrame()
        self.footer.setProperty("class", "footer")
        self.footer.setGeometry(QtCore.QRect(0, 530, 741, 61))
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)

        layout.addWidget(self.footer)

        self.setLayout(layout)        

        self.setGeometry(200, 200, 250, 150)
        self.setWindowTitle('QWebEngineView')
        self.show()

    def loadPage(self):

        with open('graph_example.html', 'r') as f:

            html = f.read()
            self.webEngineView.setHtml(html)