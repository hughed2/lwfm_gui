import threading
import time

from PyQt6.QtWidgets import (QWidget, QDateTimeEdit, QCalendarWidget,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QDialog, QSpacerItem,
                             QLabel, QTableWidget, QTableWidgetItem, QTableView)
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon, QPixmap
from widgets.FilteredTable import FilteredTable
from PyQt6.QtCore import QDateTime
from PyQt6.QtCore import Qt

from lwfm.base.Site import Site

class JobStatusWidget(QWidget):
    name = "Job Status"
    
    def __init__(self, parent):
        super().__init__(parent)

        self.setMaximumSize(QtCore.QSize(10000, 10000))

        self.live = QIcon("icons/green-circle.png")
        self.not_live = QIcon("icons/red-circle.png")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)

        #How can I get the contents of the header centered in the headerWrapperLayout?

        self.headerWrapper = QtWidgets.QWidget()
        self.headerWrapper.setProperty("class", "header")
        self.headerWrapper.setContentsMargins(0, 0, 0, 0)

        self.headerWrapperLayout = QtWidgets.QHBoxLayout(self.headerWrapper)
        self.headerWrapperLayout.setContentsMargins(0, 0, 0, 0)

        self.header = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        
        self.headerLayout = QtWidgets.QHBoxLayout(self.header)
        self.headerLayout.setSpacing(40)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        
        self.headerLabel = QtWidgets.QLabel("Job Status")
        self.headerLabel.setProperty("class", "header")
        self.headerLayout.addWidget(self.headerLabel)
        
        self.liveIndicator = QtWidgets.QWidget()
        
        self.liveIndicatorLayout = QtWidgets.QHBoxLayout(self.liveIndicator)
        self.liveIndicatorLayout.setSpacing(5)
        self.liveIndicatorLayout.setContentsMargins(0, 0, 0, 0)
        
        self.liveIndicatorLabel = QtWidgets.QLabel("Live Data")
        self.liveIndicatorLabel.setProperty("class", "liveIndicatorLabel")
        
        self.indicator = QtWidgets.QLabel()
        self.liveIndicatorLayout.addWidget(self.liveIndicatorLabel)
        self.liveIndicatorLayout.addWidget(self.indicator)
        
        self.headerLayout.addWidget(self.liveIndicator)
        
        self.headerWrapperLayout.addWidget(self.header)
        self.headerWrapperLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.headerWrapper)

        data = []
        headers = ["ID", "Status", "Site Name", "Job Name", "User Name", "Group", "Compute Type", "Timestamp"]
        self.table = FilteredTable(data, headers)
        self.table.rowClicked.connect(self.rowClicked)

        table_view = self.table.get_table_view()
        table_view.setColumnWidth(0, 280)
        table_view.setColumnWidth(1, 150)
        table_view.setColumnWidth(2, 150)
        table_view.setColumnWidth(3, 250)
        table_view.setColumnWidth(4, 130)
        table_view.setColumnWidth(5, 130)
        table_view.setColumnWidth(6, 230)
        table_view.setColumnWidth(7, 250)

        layout.addWidget(self.table)

        self.footer = QtWidgets.QFrame()
        self.footer.setGeometry(QtCore.QRect(0, 530, 741, 61))
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setProperty("class", "footer")

        self.btnLayout = QtWidgets.QHBoxLayout(self.footer)
        self.btnLayout.setContentsMargins(0, 0, 0, 0)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Start Time and End Time need a date and time, and set beginning and end points for our display        
        self.startLabel = QLabel("Start time", self)
        self.startLabel.setProperty("class", "footer_label")

        self.btnLayout.addWidget(self.startLabel)        
        self.startDate = QtWidgets.QDateTimeEdit(QDateTime.currentDateTime())
        self.startDate.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.startDate.setCalendarPopup(True)
        self.startDate.setProperty("class", "startDate")
        self.btnLayout.addWidget(self.startDate)

        self.endLabel = QLabel("End time", self)
        self.endLabel.setProperty("class", "footer_label")

        self.btnLayout.addWidget(self.endLabel)
        self.endDate = QtWidgets.QDateTimeEdit(QDateTime.currentDateTime())
        self.endDate.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.endDate.setCalendarPopup(True)
        self.endDate.setProperty("class", "startDate")
        self.btnLayout.addWidget(self.endDate)
        
        # Submit updates our display to use supplied times
        self.submitButton = QPushButton("Submit", self)
        self.submitButton.clicked.connect(self.submit)
        self.submitButton.setProperty("class", "btn-primary")
        self.btnLayout.addWidget(self.submitButton)
        
        # Clear updates our display to go live -- this is the default
        self.clearButton = QPushButton("Clear", self)
        self.clearButton.clicked.connect(self.clear)
        self.clearButton.setProperty("class", "btn-primary")
        self.btnLayout.addWidget(self.clearButton)
        
        layout.addWidget(self.footer)

        self.setLayout(layout)
        
        self.liveUpdate() # Trigger live updates
        
    def updateTable(self, startTimestamp, endTimestamp):
        if self.parent().parent().parent():
            if self.parent().parent().parent().getSite() is not None:
                data = []
                # Each cell needs to be added individually, so do a nested loop
                # These column names currently match DT4D results, but we need to make sure they match lwfm results            
                columns = ["workflowId", "status", "siteName", "jobName", "userSSO", "group", "computeType", "localTimestamp"]
                sites = self.parent().parent().parent().getSite()
                for site in sites:
                    site = Site.getSiteInstanceFactory(site)
                    runDriver = site.getRunDriver()
                    self.jobList = runDriver.getJobList(startTimestamp, endTimestamp)
                    # Table widgets work by creating a list of lists, so construct one out of our job list
                    if self.jobList:
                        for job in self.jobList:
                            context = job.getJobContext()
                            data.append([context.getId(), job.getStatus().value, context.getSiteName(), context.getName(), context.getUser(), context.getGroup(), context.getComputeType(), job.getReceivedTime()])
                self.table.update_data(data)

    def rowClicked(self, row):
        JobStatusModalWidget(self, self.jobList[row]).exec()

    def liveUpdate(self):  
        pixmap = self.live.pixmap(15, 15)
        image = pixmap.toImage()
        new_pixmap = QPixmap.fromImage(image)
        self.indicator.setPixmap(new_pixmap)
        curTime = int(time.time() * 1000)
        startTimestamp = self.startDate.dateTime().toMSecsSinceEpoch()
        self.updateTable(startTimestamp, curTime) # we'll do an update from two hours ago to now
        self.liveTimer = threading.Timer(5, JobStatusWidget.liveUpdate, args=(self,))
        self.liveTimer.daemon = True # We need to do this or else the thread will keep running even after the app is closed
        self.liveTimer.start()

    def clear(self):
        self.table.clear_filters()
        self.liveUpdate()

    def submit(self):
        startTimestamp = self.startDate.dateTime().toMSecsSinceEpoch() # This will get the msecs to midnight of the selected day
        
        endTimestamp = self.endDate.dateTime().toMSecsSinceEpoch() # This will get the msecs to midnight of the selected day

        curTime = int(time.time() * 1000)
        
        if curTime > endTimestamp:
            pixmap = self.not_live.pixmap(15, 15)
            image = pixmap.toImage()
            new_pixmap = QPixmap.fromImage(image)
            self.indicator.setPixmap(new_pixmap)

            self.liveTimer.cancel() # Deactivate the timer for live updates
        else:
            pixmap = self.live.pixmap(15, 15)
            image = pixmap.toImage()
            new_pixmap = QPixmap.fromImage(image)
            self.indicator.setPixmap(new_pixmap)

        self.updateTable(startTimestamp, endTimestamp)  

class JobStatusModalWidget(QDialog):
    def __init__(self, parent, job):
        super().__init__(parent)

        self.resize(600, 340)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        job_info_header = QLabel("Job Information", self)
        job_info_header.setProperty("class", "modal_header")

        self.layout.addWidget(job_info_header)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setRowCount(10)
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
        item.setText("Site:")
        self.table.setItem(6, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Compute Type:")
        self.table.setItem(7, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Set ID:")
        self.table.setItem(8, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Time Stamp:")
        self.table.setItem(9, 0, item)

        item = QtWidgets.QTableWidgetItem()
        context = job.getJobContext()
        item.setText(context.getId())
        self.table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getParentJobId())
        self.table.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getOriginJobId())
        self.table.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getUser())
        self.table.setItem(3, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getGroup())
        self.table.setItem(4, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getName())
        self.table.setItem(5, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getSiteName())
        self.table.setItem(6, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getComputeType())
        self.table.setItem(7, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(context.getJobSetId())
        self.table.setItem(8, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(job.getReceivedTime().strftime("%Y-%m-%d %H:%M:%S"))
        self.table.setItem(9, 1, item)

        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)

