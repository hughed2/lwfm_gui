import threading
import time

from PyQt6.QtWidgets import (QWidget, QDateTimeEdit, QCalendarWidget,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QDialog,
                             QLabel, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import QDate, QTime

from lwfm.base.Site import Site

class JobStatusModalWidget(QDialog):
    def __init__(self, parent, job):
        super().__init__(parent)
        
        self.layout = QVBoxLayout()
        
        label = QLabel(str(job)[:50], self)
        self.layout.addWidget(label)
        
        self.setLayout(self.layout)
    

class JobStatusWidget(QWidget):
    name = "Job Status"
    
    def __init__(self, parent):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "User Name", "Status", "Job Name"]) # Have to do this after setting row count
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.cellClicked)
        
        layout.addWidget(self.table)
        
        # We have multiple buttons we want side by side, so put them in an HBoxLayout
        btnLayout = QHBoxLayout()

        # Start Time and End Time need a date and time, and set beginning and end points for our display        
        startLabel = QLabel("Start time", self)
        btnLayout.addWidget(startLabel)        
        self.startTime = QDateTimeEdit(QTime.currentTime())
        btnLayout.addWidget(self.startTime)
        self.startDate = QDateTimeEdit(QDate.currentDate())
        self.startDate.setCalendarPopup(True)
        self.startDate.setCalendarWidget(QCalendarWidget())
        btnLayout.addWidget(self.startDate)

        endLabel = QLabel("End time", self)
        btnLayout.addWidget(endLabel)
        self.endTime = QDateTimeEdit(QTime.currentTime())
        btnLayout.addWidget(self.endTime)
        self.endDate = QDateTimeEdit(QDate.currentDate())
        self.endDate.setCalendarPopup(True)
        self.endDate.setCalendarWidget(QCalendarWidget())
        btnLayout.addWidget(self.endDate)
        
        # Submit updates our display to use supplied times
        submitButton = QPushButton("Submit", self)
        submitButton.clicked.connect(self.submit)
        btnLayout.addWidget(submitButton)
        
        # Clear updates our display to go live -- this is the default
        clearButton = QPushButton("Clear", self)
        clearButton.clicked.connect(self.liveUpdate)
        btnLayout.addWidget(clearButton)
        
        layout.addLayout(btnLayout)
        self.setLayout(layout)
        
        self.liveUpdate() # Trigger live updates
        
    def updateTable(self, startTimestamp, endTimestamp):
        site = self.parent().parent().getSite()
        if site is not None:
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
                self.table.setItem(idx, 0, QTableWidgetItem(job.getJobContext().getNativeId()))
                self.table.setItem(idx, 1, QTableWidgetItem('USERNAME (not part of lwfm)'))
                self.table.setItem(idx, 2, QTableWidgetItem(job.getNativeStatusStr()))
                self.table.setItem(idx, 3, QTableWidgetItem(job.getJobContext().getName()))
                    
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
        

