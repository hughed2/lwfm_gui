import threading
import time

from PyQt6.QtWidgets import (QWidget, QDateTimeEdit, QCalendarWidget,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QDialog, QSpacerItem,
                             QLabel, QTableWidget, QTableWidgetItem, QTableView)
from PyQt6 import QtCore, QtGui, QtWidgets
from widgets.FilteredTable import FilteredTable
from PyQt6.QtCore import QDateTime

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

        self.header = QtWidgets.QLabel()

        layout.addWidget(self.header)

        data = []
        headers = ["ID", "Status", "Job Name", "User Name", "Group", "Compute Type", "Timestamp"]
        self.table = FilteredTable(data, headers)
        self.table.rowClicked.connect(self.rowClicked)


        layout.addWidget(self.table)

        self.footer = QtWidgets.QFrame()

        # We have multiple buttons we want side by side, so put them in an HBoxLayout
        #btnLayout = QHBoxLayout()

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.footer)
        self.btnLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)

        # Start Time and End Time need a date and time, and set beginning and end points for our display        
        self.startLabel = QLabel("Start time", self)

        self.btnLayout.addWidget(self.startLabel)        
        self.startDate = QDateTimeEdit(QDateTime.currentDateTime())
        self.btnLayout.addWidget(self.startDate)

        self.endLabel = QLabel("End time", self)
        self.btnLayout.addWidget(self.endLabel)
        self.endDate = QDateTimeEdit(QDateTime.currentDateTime())
        self.btnLayout.addWidget(self.endDate)
        
        # Submit updates our display to use supplied times
        self.submitButton = QPushButton("Submit", self)
        self.submitButton.clicked.connect(self.submit)
        self.btnLayout.addWidget(self.submitButton)
        
        # Clear updates our display to go live -- this is the default
        self.clearButton = QPushButton("Clear", self)
        self.clearButton.clicked.connect(self.liveUpdate)
        self.btnLayout.addWidget(self.clearButton)

        self.spacerItem = QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.btnLayout.addItem(self.spacerItem)
        
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

                # Each cell needs to be added individually, so do a nested loop
                # These column names currently match DT4D results, but we need to make sure they match lwfm results            
                columns = ["workflowId", "status", "jobName", "userSSO", "group", "computeType", "localTimestamp"]
                data = []
                for idx, job in enumerate(displayedJobs):
                    row = []
                    for idx2, column in enumerate(columns):
                        row.append(job[column])
                    data.append(row)
                self.table.update_data(data)

    def rowClicked(self, row):
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
        
        endTimestamp = self.endDate.dateTime().toMSecsSinceEpoch() # This will get the msecs to midnight of the selected day

        self.updateTable(startTimestamp, endTimestamp)  


        
    def setStyles(self):        
        self.header.setGeometry(QtCore.QRect(-2, 10, 751, 54))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setMaximumSize(QtCore.QSize(table_width, 54))
        self.header.setStyleSheet("background-color: rgb(0, 151, 255);color: rgb(255, 255, 255);")
        self.header.setFont(font)
        self.header.setText("Job Status")
        self.header.setProperty("class", "header")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.table.sizePolicy().hasHeightForWidth())
        self.table.setSizePolicy(sizePolicy)
        self.table.setMaximumSize(QtCore.QSize(table_width, 10000))

        self.footer.setGeometry(QtCore.QRect(0, 530, 741, 61))
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setProperty("class", "footer")

        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 741, 41))

        self.btnLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.btnLayout.setContentsMargins(0, 0, 0, 0)

        self.startLabel.setProperty("class", "footer_label")
        self.startLabel.setFont(font)
        self.startLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.startLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.startDate.setCalendarPopup(True)
        self.startDate.setCalendarWidget(QCalendarWidget())
        self.startDate.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.endLabel.setProperty("class", "footer_label")
        self.endLabel.setFont(font)
        self.endLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.endLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.endDate.setCalendarPopup(True)
        self.endDate.setCalendarWidget(QCalendarWidget())
        self.endDate.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.submitButton.setProperty("class", "btn-primary")
        self.submitButton.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.clearButton.setProperty("class", "btn-primary")
        self.clearButton.setStyleSheet("background-color: rgb(255, 255, 255);")

class JobStatusModalWidget(QDialog):
    def __init__(self, parent, job):
        super().__init__(parent)

        self.resize(600, 305)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        job_info_header = QLabel("Job Information", self)
        job_info_header.setProperty("class", "modal_header")

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

