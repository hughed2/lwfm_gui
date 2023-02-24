import threading
import time

from PyQt6.QtWidgets import (QWidget, QDateTimeEdit, QCalendarWidget,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QDialog,
                             QLabel, QTableWidget, QTableWidgetItem, QTableView)
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QDate, QTime

from lwfm.base.Site import Site

font = QtGui.QFont()
font.setFamily("Helvetica Neue")

table_width = 10000
column_width = 300
table_height = 10000
column_count = 7

class JobStatusWidget(QWidget):
    name = "Job Status"
    
    def __init__(self, parent):
        super().__init__(parent)

        self.setMaximumSize(QtCore.QSize(table_width, table_height))

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)

        self.status_header = QtWidgets.QLabel()

        layout.addWidget(self.status_header)

        self.table = QTableWidget()
        
        self.table.cellClicked.connect(self.cellClicked)

        layout.addWidget(self.table)

        self.footer = QtWidgets.QFrame()

        # We have multiple buttons we want side by side, so put them in an HBoxLayout
        #btnLayout = QHBoxLayout()

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.footer)
        self.btnLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)

        # Start Time and End Time need a date and time, and set beginning and end points for our display        
        self.startLabel = QLabel("Start time", self)

        self.btnLayout.addWidget(self.startLabel)        
        self.startTime = QDateTimeEdit(QTime.currentTime())
        self.btnLayout.addWidget(self.startTime)
        self.startDate = QDateTimeEdit(QDate.currentDate())
        self.btnLayout.addWidget(self.startDate)

        self.endLabel = QLabel("End time", self)
        self.btnLayout.addWidget(self.endLabel)
        self.endTime = QDateTimeEdit(QTime.currentTime())
        self.btnLayout.addWidget(self.endTime)
        self.endDate = QDateTimeEdit(QDate.currentDate())
        self.btnLayout.addWidget(self.endDate)
        
        # Submit updates our display to use supplied times
        self.submitButton = QPushButton("Submit", self)
        self.submitButton.clicked.connect(self.submit)
        self.btnLayout.addWidget(self.submitButton)
        
        # Clear updates our display to go live -- this is the default
        self.clearButton = QPushButton("Clear", self)
        self.clearButton.clicked.connect(self.liveUpdate)
        self.btnLayout.addWidget(self.clearButton)
        
        layout.addWidget(self.footer)

        self.setStyles()

        self.setLayout(layout)
        
        self.liveUpdate() # Trigger live updates
        
    def updateTable(self, startTimestamp, endTimestamp):
        if self.parent().parent().parent():
            if self.parent().parent().parent().getSite() is not None:
                site = self.parent().parent().parent().getSite()
                site = Site.getSiteInstanceFactory(site)
                runDriver = site.getRunDriver()
                self.jobList = runDriver.getJobList(startTimestamp, endTimestamp)

                # Table widgets work by creating a list of lists, so construct one out of our job list
                numDisplayed = min(len(self.jobList), 50) # Display the first 50--should be more modular for pagination
                displayedJobs = self.jobList[0:numDisplayed] 
                self.table.setRowCount(numDisplayed)

                # Each cell needs to be added individually, so do a nested loop
                # These column names currently match DT4D results, but we need to make sure they match lwfm results            
                columns = ["id", "status", "jobName", "userSSO", "group", "computeType", "localTimestamp"]
                for idx, job in enumerate(displayedJobs):
                    for idx2, column in enumerate(columns):
                        self.table.setItem(idx, idx2, QTableWidgetItem(job[column]))
                        
                # We might not have a full set of 50, so clear the rest of the contents
                for idx in range(numDisplayed, 50):
                    for idx2 in range(len(columns)):
                        self.table.setItem(idx, idx2, QTableWidgetItem(""))

    def cellClicked(self, row, column):
        JobStatusModalWidget(self, self.jobList[row]).exec()


    def liveUpdate(self):
        curTime = int(time.time() * 1000)
        self.updateTable(curTime - (2 * 60 * 60 * 1000), curTime) # we'll do an update from two hours ago to now
        self.liveTimer = threading.Timer(5, JobStatusWidget.liveUpdate, args=(self,))
        self.liveTimer.daemon = True # We need to do this or else the thread will keep running even after the app is closed
        self.liveTimer.start()
        
    def submit(self):
        self.liveTimer.cancel() # Deactivate the timer for live updates
        
        startTimestamp = self.startDate.dateTime().toMSecsSinceEpoch() # This will get the msecs to midnight of the selected day
        startTimestamp += self.startTime.time().msec() # This will get the msecs from midnight to the selected time
        
        endTimestamp = self.endDate.dateTime().toMSecsSinceEpoch() # This will get the msecs to midnight of the selected day
        endTimestamp += self.endTime.time().msec() # This will get the msecs from midnight to the selected time
        
        self.updateTable(startTimestamp, endTimestamp)        
        
    def setStyles(self):        
        self.status_header.setGeometry(QtCore.QRect(-2, 10, 751, 54))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.status_header.sizePolicy().hasHeightForWidth())
        self.status_header.setSizePolicy(sizePolicy)
        self.status_header.setMaximumSize(QtCore.QSize(table_width, 54))
        self.status_header.setStyleSheet("background-color: rgb(0, 151, 255);color: rgb(255, 255, 255);")
        self.status_header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_header.setFont(font)
        self.status_header.setText("Job Status")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.status_header.sizePolicy().hasHeightForWidth())
        self.status_header.setSizePolicy(sizePolicy)
        self.status_header.setMaximumSize(QtCore.QSize(table_width, 54))

        self.table.setColumnCount(column_count)
        "id", "status", "jobName", "userSSO", "group", "computeType", "localTimestamp"
        self.table.setHorizontalHeaderLabels(["ID", "Status", "Job Name", "User Name", "Group", "Compute Type", "Timestamp"]) # Have to do this after setting row count
        self.table.horizontalHeader().setStyleSheet("QHeaderView { font-size: 16pt; }")
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setGeometry(QtCore.QRect(0, 60, 749, 471))
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
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.table.sizePolicy().hasHeightForWidth())
        self.table.setSizePolicy(sizePolicy)
        self.table.setMaximumSize(QtCore.QSize(table_width, 10000))

        self.footer.setGeometry(QtCore.QRect(0, 530, 741, 61))
        self.footer.setStyleSheet("background-color: rgb(0, 151, 255);")
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setMaximumSize(QtCore.QSize(table_width, 54))

        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 741, 41))

        self.btnLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.btnLayout.setContentsMargins(0, 0, 0, 0)

        self.startLabel.setFont(font)
        self.startLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.startLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.startTime.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.startDate.setCalendarPopup(True)
        self.startDate.setCalendarWidget(QCalendarWidget())
        self.startDate.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.endLabel.setFont(font)
        self.endLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.endLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.endTime.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.endDate.setCalendarPopup(True)
        self.endDate.setCalendarWidget(QCalendarWidget())
        self.endDate.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.submitButton.setMaximumSize(QtCore.QSize(50, 30))
        self.submitButton.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.clearButton.setMaximumSize(QtCore.QSize(50, 30))
        self.clearButton.setStyleSheet("background-color: rgb(255, 255, 255);")

class JobStatusModalWidget(QDialog):
    def __init__(self, parent, job):
        super().__init__(parent)

        self.resize(600, 300)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        print(str(job))
        
        job_info_header = QLabel("Job Information", self)
        job_info_header.setMaximumSize(QtCore.QSize(600, 54))
        job_info_header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        job_info_header.setStyleSheet("background-color: rgb(1, 26, 40);color: rgb(255, 255, 255);")
        job_info_header.setFont(font)
        self.layout.addWidget(job_info_header)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setRowCount(9)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultSectionSize(300)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        item = QtWidgets.QTableWidgetItem()
        item.setText("Job ID:")
        self.table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Parent ID:")
        self.table.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Originator ID:")
        self.table.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("User:")
        self.table.setItem(3, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Group:")
        self.table.setItem(4, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Job Name:")
        self.table.setItem(5, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Compute Type:")
        self.table.setItem(6, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Set ID:")
        self.table.setItem(7, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Time Stamp:")
        self.table.setItem(8, 0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(job["workflowId"])
        self.table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["parentWorkflowId"])
        self.table.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["originatorWorkflowId"])
        self.table.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["userSSO"])
        self.table.setItem(3, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["group"])
        self.table.setItem(4, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["jobName"])
        self.table.setItem(5, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["computeType"])
        self.table.setItem(6, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["partOfSet"])
        self.table.setItem(7, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job["localTimestamp"])
        self.table.setItem(8, 1, item)

        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)

