import threading
import time

from PyQt6.QtWidgets import (QWidget, QDateTimeEdit, QCalendarWidget,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QDialog,
                             QLabel, QTableWidget, QTableWidgetItem)
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QDate, QTime

from lwfm.base.Site import Site

class TriggerModalWidget(QDialog):
    def __init__(self, parent, job):
        super().__init__(parent)
        
        self.layout = QVBoxLayout()
        
        label = QLabel(str(job)[:50], self)
        self.layout.addWidget(label)
        
        self.setLayout(self.layout)

class TriggerWidget(QWidget):
    name = "Trigger List"
    
    def __init__(self, parent):
        super().__init__(parent)

        table_width = 10000
        column_width = 300
        table_height = 10000
        column_count = 4

        self.setMaximumSize(QtCore.QSize(table_width, table_height))
        
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
        self.header.setText(_translate("MainWindow", "Triggers"))

        layout.addWidget(self.header)

        self.table = QTableWidget()
        self.table.setColumnCount(column_count)
        self.table.setHorizontalHeaderLabels(["ID", "User Name", "Status", "Job Name"]) # Have to do this after setting row count
        self.table.horizontalHeader().setStyleSheet("QHeaderView { font-size: 16pt; }")
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setGeometry(QtCore.QRect(0, 60, 749, 471))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setMaximumSize(QtCore.QSize(table_width, 54))
        
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(229, 234, 248))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(229, 234, 248))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(229, 234, 248))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.AlternateBase, brush)
        self.table.setPalette(palette)
        self.table.horizontalHeader().setVisible(True)
        self.table.horizontalHeader().setCascadingSectionResizes(False)
        self.table.horizontalHeader().setDefaultSectionSize(column_width)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setCascadingSectionResizes(False)
        self.table.verticalHeader().setStretchLastSection(False)
        self.table.cellClicked.connect(self.cellClicked)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.table.sizePolicy().hasHeightForWidth())
        self.table.setSizePolicy(sizePolicy)
        self.table.setMaximumSize(QtCore.QSize(table_width, 10000))

        layout.addWidget(self.table)

        self.footer = QtWidgets.QFrame()
        self.footer.setProperty("class", "footer")
        self.footer.setGeometry(QtCore.QRect(0, 530, 741, 61))
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setMaximumSize(QtCore.QSize(table_width, 54))

        # We have multiple buttons we want side by side, so put them in an HBoxLayout
        #btnLayout = QHBoxLayout()

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.footer)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 741, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.btnLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.btnLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.btnLayout.setContentsMargins(0, 0, 0, 0)
        self.btnLayout.setObjectName("horizontalLayout")
        
        # Submit updates our display to use supplied times
        submitButton = QPushButton("Submit", self)
        submitButton.setMaximumSize(QtCore.QSize(50, 30))
        submitButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        submitButton.clicked.connect(self.submit)
        self.btnLayout.addWidget(submitButton)
        
        # Clear updates our display to go live -- this is the default
        clearButton = QPushButton("Clear", self)
        clearButton.setMaximumSize(QtCore.QSize(50, 30))
        clearButton.clicked.connect(self.liveUpdate)
        clearButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.btnLayout.addWidget(clearButton)
        
        layout.addWidget(self.footer)

        self.setLayout(layout)
        
        self.liveUpdate() # Trigger live updates
        
    def updateTable(self, startTimestamp, endTimestamp):
        if self.parent().parent().parent():
            site = self.parent().parent().parent().getSite()
            if site: # Don't continue if we haven't chosen any sites
                if isinstance(site, list): # If we have a list of sites, only display one at a time--should be changed later, this was just to fix a bug
                    site = site[0]
                site = Site.getSiteInstanceFactory(site)
                runDriver = site.getRunDriver()
                self.jobList = runDriver.getJobList(startTimestamp, endTimestamp)

                # Table widgets work by creating a list of lists, so construct one out of our job list
                numDisplayed = min(len(self.jobList), 50) # Display the first 50--should be more modular for pagination
                displayedJobs = self.jobList[0:numDisplayed] 
                self.table.setRowCount(numDisplayed)

                # Each cell needs to be added individually, so do a nested loop
                # These column names currently match DT4D results, but we need to make sure they match lwfm results            
                columns = ["id", "userSSO", "status", "jobName"]
                for idx, job in enumerate(displayedJobs):
                    for idx2, column in enumerate(columns):
                        self.table.setItem(idx, idx2, QTableWidgetItem(job[column]))
                        
                # We might not have a full set of 50, so clear the rest of the contents
                for idx in range(numDisplayed, 50):
                    for idx2 in range(len(columns)):
                        self.table.setItem(idx, idx2, QTableWidgetItem(""))

    def cellClicked(self, row, column):
        TriggerModalWidget(self, self.jobList[row]).exec()


    def liveUpdate(self):
        curTime = int(time.time() * 1000)
        self.updateTable(curTime - (2 * 60 * 60 * 1000), curTime) # we'll do an update from two hours ago to now
        self.liveTimer = threading.Timer(5, TriggerWidget.liveUpdate, args=(self,))
        self.liveTimer.daemon = True # We need to do this or else the thread will keep running even after the app is closed
        self.liveTimer.start()
        
    def submit(self):
        self.liveTimer.cancel() # Deactivate the timer for live updates
        
        startTimestamp = self.startDate.dateTime().toMSecsSinceEpoch() # This will get the msecs to midnight of the selected day
        startTimestamp += self.startTime.time().msec() # This will get the msecs from midnight to the selected time
        
        endTimestamp = self.endDate.dateTime().toMSecsSinceEpoch() # This will get the msecs to midnight of the selected day
        endTimestamp += self.endTime.time().msec() # This will get the msecs from midnight to the selected time
        
        self.updateTable(startTimestamp, endTimestamp) 
