from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget

class NavBar(QWidget):
    name = "NavBar"
    
    def __init__(self, parent):
        super().__init__(parent)
        _translate = QtCore.QCoreApplication.translate

        self.navbarIndices = {"Set Site":0, "Job Status": 1, "Triggers": 2, "Meta Tree View": 3, "Graph": 4}

        font = QtGui.QFont()
        font.setFamily("Helvetica Neue")

        self.verticalLayoutWidget = QtWidgets.QWidget()
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 102, 581))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayoutWidget.setMaximumSize(QtCore.QSize(150, 10000))
        self.verticalLayoutWidget.setStyleSheet("background-color: rgb(1, 26, 40);")
        self.navLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.navLayout.setContentsMargins(0, 0, 0, 0)
        self.navLayout.setSpacing(0)
        self.navLayout.setObjectName("navLayout")
        self.logo = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(sizePolicy)
        self.logo.setMaximumSize(QtCore.QSize(150, 100))
        self.logo.setStyleSheet("background-color: rgb(1, 26, 40);padding:0px 25px;")
        self.logo.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.logo.setPixmap(QtGui.QPixmap("img/ge_monogram_primary_white_CMYK.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.navLayout.addWidget(self.logo)
        self.navbar = QtWidgets.QListWidget(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.navbar.sizePolicy().hasHeightForWidth())
        self.navbar.setSizePolicy(sizePolicy)
        self.navbar.setMaximumSize(QtCore.QSize(150, 10000))
        self.navbar.setAcceptDrops(False)
        self.navbar.setAutoFillBackground(False)
        self.navbar.setStyleSheet("font: 14pt \"Helvetica Neue\";\n"
"background-color: rgb(1, 26, 40);\n"
"alternate-background-color: rgb(193, 255, 255);\n"
"selection-background-color: rgb(1, 26, 40);\n"
"selection-color: rgb(170, 245, 255);")
        self.navbar.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.navbar.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.navbar.setLineWidth(0)
        self.navbar.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.navbar.setProperty("showDropIndicator", False)
        self.navbar.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.navbar.setLayoutMode(QtWidgets.QListView.LayoutMode.SinglePass)
        self.navbar.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.navbar.setModelColumn(0)
        self.navbar.setUniformItemSizes(True)
        self.navbar.setBatchSize(54)
        self.navbar.setSelectionRectVisible(False)
        self.navbar.setObjectName("navbar")
        self.navbar.setSpacing(15)
        self.navbar.itemClicked.connect(self.listwidgetclicked)

        item = QtWidgets.QListWidgetItem()
        item.setForeground(QtGui.QColor(255, 255, 255))
        item.setFont(font)
        item.setText(_translate("MainWindow", "Set Site"))
        self.navbar.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setForeground(QtGui.QColor(255, 255, 255))
        item.setFont(font)
        item.setText(_translate("MainWindow", "Job Status"))
        self.navbar.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setForeground(QtGui.QColor(255, 255, 255))
        item.setFont(font)
        item.setText(_translate("MainWindow", "Triggers"))
        self.navbar.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setForeground(QtGui.QColor(255, 255, 255))
        item.setFont(font)
        item.setText(_translate("MainWindow", "Meta Tree View"))
        self.navbar.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setForeground(QtGui.QColor(255, 255, 255))
        item.setFont(font)
        item.setText(_translate("MainWindow", "Graph"))
        self.navbar.addItem(item)
        self.navLayout.addWidget(self.navbar)
        self.setLayout(self.navLayout)

    def listwidgetclicked(self, item):
        self.parent().parent().changePage(self.navbarIndices[item.text()])
