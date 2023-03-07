from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QToolBar
from PyQt6.QtGui import QAction
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QWidget, QDateTimeEdit, QCalendarWidget,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QDialog,
                             QLabel, QTableWidget, QTableWidgetItem)

from Views import SiteView, JobStatusView, TriggerView, NavBar, MetaTreeView, Graph

class MainWindow(QMainWindow):
    stack = None
    toolbar = None
    currentSite = None

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("lwfm")

        self.frameLayoutWidget = QtWidgets.QWidget()
        self.frameLayout = QtWidgets.QHBoxLayout(self.frameLayoutWidget)
        self.frameLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.frameLayout.setContentsMargins(0, 0, 0, 0)
        self.frameLayout.setSpacing(0)

        # Our stack is our list of pages we might see--make it from a list of widgets so we can automate it
        self.stack = QStackedWidget(self)
        widgets = [SiteView.SiteWidget, JobStatusView.JobStatusWidget, TriggerView.TriggerWidget, MetaTreeView.MetaTreeViewWidget, Graph.GraphWidget]
        
        for idx, widget in enumerate(widgets):
           self.stack.addWidget(widget(self.stack))

        self.navBar = NavBar.NavBar(self)
        self.frameLayout.addWidget(self.navBar)
        self.frameLayout.addWidget(self.stack)
        self.showMaximized()
        self.setCentralWidget(self.frameLayoutWidget)
        #self.changePage(3)
        self.disableToolbar() # We don't want them to choose a new page until they've chosen their site

    def changePage(self, idx):
        self.stack.setCurrentIndex(idx)
        
    def disableToolbar(self):
        self.navBar.setDisabled(True)

    def enableToolbar(self):
        self.navBar.setDisabled(False)
            
    def setSite(self, site):
        self.currentSite = site
        if site is None:
            self.disableToolbar()
        else:
            self.enableToolbar()
            
    def getSite(self):
        return self.currentSite
