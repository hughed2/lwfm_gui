import sys

from PyQt6.QtWidgets import QWidget, QPushButton, QRadioButton, QVBoxLayout

from lwfm.base.Site import Site

sys.path.append('..')
from Utils import msgBox

class SiteWidget(QWidget):
    name = "Set Site"
    
    def __init__(self, parent):
        super().__init__(parent)
        
        layout = QVBoxLayout()

        # Loop isn't working -- not bothing to figure out now since it might get rewritten
        self.btn1 = QRadioButton("dt4d")
        self.btn1.toggled.connect(lambda:self.btnstate(self.btn1))
        layout.addWidget(self.btn1)
        self.btn2 = QRadioButton("cori")
        self.btn2.toggled.connect(lambda:self.btnstate(self.btn2))
        layout.addWidget(self.btn2)
        self.btn3 = QRadioButton("perlmutter")
        self.btn3.toggled.connect(lambda:self.btnstate(self.btn3))
        layout.addWidget(self.btn3)
        self.btn4 = QRadioButton("local")
        self.btn4.toggled.connect(lambda:self.btnstate(self.btn4))
        layout.addWidget(self.btn4)
        
        self.btn5 = QPushButton("Add Site") # Doesn't do anything right now
        layout.addWidget(self.btn5)

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
                self.parent().parent().setSite(None)
                return
        msgBox(f"Successfully logged in to site {b.text()}", self)
        self.parent().parent().setSite(b.text())
