from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QToolBar
from PyQt6.QtGui import QAction

from Views import SiteView, JobStatusView, TriggerView

class MainWindow(QMainWindow):
    stack = None
    toolbar = None
    currentSite = None

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("lwfm")

        # Initialize a toolbar, we'll add to it later        
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Our stack is our list of pages we might see--make it from a list of widgets so we can automate it
        self.stack = QStackedWidget(self)
        widgets = [SiteView.SiteWidget, JobStatusView.JobStatusWidget, TriggerView.TriggerWidget]
        
        for idx, widget in enumerate(widgets):
           button = QAction(widget.name, self)
           button.triggered.connect(lambda checked, index=idx: self.changePage(index))
           self.toolbar.addAction(button)
           self.stack.addWidget(widget(self.stack))
           
        self.setCentralWidget(self.stack)
        self.disableToolbar() # We don't want them to choose a new page until they've chosen their site

    def changePage(self, idx):
        self.stack.setCurrentIndex(idx)
        
    def disableToolbar(self):
        for button in self.toolbar.actions():
            button.setDisabled(True)

    def enableToolbar(self):
        for button in self.toolbar.actions():
            button.setDisabled(False)
            
    def setSite(self, site):
        self.currentSite = site
        if site is None:
            self.disableToolbar()
        else:
            self.enableToolbar()
            
    def getSite(self):
        return self.currentSite
