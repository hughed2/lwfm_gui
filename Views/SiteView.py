import sys

from PyQt6.QtWidgets import QWidget, QPushButton, QRadioButton, QVBoxLayout
from PyQt6 import QtCore, QtGui, QtWidgets

from lwfm.base.Site import Site

sys.path.append('..')
from Utils import msgBox

class SiteWidget(QWidget):
    name = "Set Site"
    
    def __init__(self, parent):
        super().__init__(parent)

        _translate = QtCore.QCoreApplication.translate
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)

        self.header = QtWidgets.QLabel()
        self.header.setProperty("class", "header")
        self.header.setGeometry(QtCore.QRect(-2, 10, 751, 54))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setText(_translate("MainWindow", "Site Selection"))

        layout.addWidget(self.header)

        self.site_selection_frame = QtWidgets.QFrame()
        self.site_selection_frame.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 16pt \"Helvetica Neue\";")

        self.btnLayout = QtWidgets.QVBoxLayout(self.site_selection_frame)
        self.btnLayout.setContentsMargins(20, 20, 20, 20)
        self.btnLayout.setSpacing(20)
        self.btnLayout.setObjectName("navLayout")

        # Loop isn't working -- not bothing to figure out now since it might get rewritten
        self.btn1 = QRadioButton("dt4d")
        self.btn1.toggled.connect(lambda:self.btnstate(self.btn1))
        self.btnLayout.addWidget(self.btn1)
        self.btn2 = QRadioButton("cori")
        self.btn2.toggled.connect(lambda:self.btnstate(self.btn2))
        self.btnLayout.addWidget(self.btn2)
        self.btn3 = QRadioButton("perlmutter")
        self.btn3.toggled.connect(lambda:self.btnstate(self.btn3))
        self.btnLayout.addWidget(self.btn3)
        self.btn4 = QRadioButton("local")
        self.btn4.toggled.connect(lambda:self.btnstate(self.btn4))
        self.btnLayout.addWidget(self.btn4)
        
        self.btn5 = QPushButton("Add Site") # Doesn't do anything right now
        self.btn5.setMaximumSize(QtCore.QSize(120, 30))
        self.btn5.setStyleSheet("background-color: rgb(205, 205, 205);")
        self.btnLayout.addWidget(self.btn5)

        layout.addWidget(self.site_selection_frame)

        self.footer = QtWidgets.QFrame()
        self.footer.setProperty("class", "footer")
        self.footer.setGeometry(QtCore.QRect(0, 530, 741, 61))
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setMaximumSize(QtCore.QSize(10000, 54))

        layout.addWidget(self.footer)

        self.setLayout(layout)
        
    def btnstate(self, b):
        if not b.isChecked(): # We don't care about deselect events
            return
        site = Site.getSiteInstanceFactory(b.text())
        if not isinstance(site, Site):
            msgBox("ERROR: NON-EXISTING SITE SELECTED. PLEASE REPORT ERROR TO LWFM DEVS", self)
            return
            
        authDriver = site.getAuthDriver()
        if not authDriver.isAuthCurrent():
            authDriver.login()
            if not authDriver.isAuthCurrent():
                msgBox(f"ERROR: Could not log in to site {b.text()}", self)
                self.parent().parent().parent().setSite(None)
                return
        msgBox(f"Successfully logged in to site {b.text()}", self)
        self.parent().parent().parent().setSite(b.text())
