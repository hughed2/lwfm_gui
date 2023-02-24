import threading
import time
import json
import requests
from datetime import datetime

from PyQt6.QtWidgets import (QWidget, QDateTimeEdit, QCalendarWidget,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QDialog,
                             QLabel, QTableWidget, QTableWidgetItem, 
                             QTableView, QSpacerItem, QScrollArea, QFileDialog, QHeaderView)
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QDateTime, QTime

from pathlib import Path

from lwfm.base.Site import Site  
from lwfm.base.SiteFileRef import FSFileRef  

max_size = 10000

font = QtGui.QFont()
font.setFamily("Helvetica Neue")

class MetaTreeViewWidget(QWidget):
    name = "Meta Tree View"
    
    def __init__(self, parent):
        super().__init__(parent)

        if self.parent().parent().getSite() is not None:
            site = self.parent().parent().getSite()
            site = Site.getSiteInstanceFactory(site)
            self.repoDriver = site.getRepoDriver()
        else:
            site = Site.getSiteInstanceFactory("dt4d")
            self.repoDriver = site.getRepoDriver()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
#-------Header
        self.mtv_header = QtWidgets.QLabel()
        layout.addWidget(self.mtv_header)
#-------Main Page
        self.mtv = QtWidgets.QWidget()
        self.mtv.setObjectName("mtv")

        self.main_layout = QtWidgets.QVBoxLayout(self.mtv)

        self.tree_form = QtWidgets.QWidget()

        self.tree_form_layout = QtWidgets.QVBoxLayout(self.tree_form)

        self.scroll = QScrollArea(self)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()

        self.tree_inputs_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
       
        self.scroll.setWidget(self.scrollAreaWidgetContents)

        self.tree_form_layout.addWidget(self.scroll)

        self.add_button = QtWidgets.QPushButton(self.mtv)
        self.add_button.clicked.connect(self.add_input)

        self.tree_form_layout.addWidget(self.add_button)
        self.main_layout.addWidget(self.tree_form)

        self.mtv_form = QtWidgets.QWidget()

        self.mtv_layout = QtWidgets.QHBoxLayout(self.mtv_form)
        self.mtv_layout.setSpacing(0)

        self.mtv_tree = QtWidgets.QTreeWidget(self.mtv)
        self.mtv_layout.addWidget(self.mtv_tree)
        
        self.table = QtWidgets.QTableWidget()
        self.table.cellClicked.connect(self.cellClicked)
        self.mtv_layout.addWidget(self.table)

        self.main_layout.addWidget(self.mtv_form)

        layout.addWidget(self.mtv)
#-------Footer
        self.footer = QtWidgets.QFrame()

        self.footerLayoutWidget = QtWidgets.QWidget(self.footer)
        self.btnLayout = QtWidgets.QHBoxLayout(self.footerLayoutWidget)

        self.tenant_label = QtWidgets.QLabel()
        self.btnLayout.addWidget(self.tenant_label)

        self.tenant_selection = QtWidgets.QComboBox()
        self.btnLayout.addWidget(self.tenant_selection)
        
        self.start_label = QtWidgets.QLabel()
        self.btnLayout.addWidget(self.start_label)
        
        self.start_date = QtWidgets.QDateTimeEdit(QDateTime.currentDateTime())
        self.btnLayout.addWidget(self.start_date)

        self.end_label = QtWidgets.QLabel()
        self.btnLayout.addWidget(self.end_label)
        
        self.end_date = QtWidgets.QDateTimeEdit(QDateTime.currentDateTime())
        self.btnLayout.addWidget(self.end_date)

        self.submitButton = QPushButton("Create Tree", self)
        self.submitButton.clicked.connect(self.submit)
        self.btnLayout.addWidget(self.submitButton)

        self.file_browser_button = QtWidgets.QPushButton()
        self.file_browser_button.clicked.connect(self.get_file)
        #self.btnLayout.addWidget(self.file_browser_button)

        self.spacerItem = QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.btnLayout.addItem(self.spacerItem)
        
        layout.addWidget(self.footer)

        self.setStyles()

        self.setLayout(layout)

        #self.tree_inputs_layout.addWidget(TreeInput(self))
        self.tree_inputs_layout.addWidget(TreeInput(self, "GradyTest"))
        self.tree_inputs_layout.addWidget(TreeInput(self, "project"))
        self.tree_inputs_layout.addWidget(TreeInput(self, "case")) 

    def submit(self):
        #Remove the previous tree if it exists
        self.mtv_tree.clear()
        #Getting the top level fields to create the top level part of the tree
        field = self.tree_inputs_layout.itemAt(0).widget().get_tree_field()
        contains = self.tree_inputs_layout.itemAt(0).widget().get_contains_field()
        #Getting the list of values that match the top level criteria
        values = self.get_values(field, contains)
        #Creating Items for each value
        for x in range(len(values)):
            item = QtWidgets.QTreeWidgetItem(self.mtv_tree)
            self.mtv_tree.topLevelItem(x).setText(0, values[x])
            #adding an empty item as a child of this item so that it is expandable.  This will be replaced by the 
            #next level of the tree if the user clicks the expand.
            item2 = QtWidgets.QTreeWidgetItem(item)
        
    def add_input(self, txt=None):
        #Adds a TreeInput the the tree input list
        tree_input = TreeInput(self, txt)
        self.tree_inputs_layout.addWidget(TreeInput(self))

    #currently just an example method for opening a file dialog and reading its data.  Not actually used right now.
    def get_file(self):
        home_dir = str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:

            f = open(fname[0], 'r')

            with f:

                data = f.read()
                print(data)

    def treeItemExpand(self, it):
        # We need to remove the children of this item because if the item was collapsed it will be duplicating the items.
        # for i in reversed(range(it.childCount())):
        #     it.removeChild(it.child(i))

        #The tree item expand doesn't provide the column (tree level) of the item, we will need to know so that we know
        #which input field its associated with to get the next set of values of its children.
        column_index = 0
        parent = it.parent()
        while(parent):
            column_index = column_index + 1
            parent = parent.parent()

        #Getting the field for the corresponding input and its value.  This will need to be included as metadata 
        #for getting the next set of values.
        field = self.tree_inputs_layout.itemAt(column_index).widget().get_tree_field()
        value = it.text(0)
        metadata = {field: value}
        parent = it.parent()

        #idx is used to iterate in reverse of the current index so that we can add all of the metadata from higher up the tree
        idx = column_index
        #loop through the parents
        for x in range(column_index):
            idx = idx - 1
            field = self.tree_inputs_layout.itemAt(idx).widget().get_tree_field()
            value = parent.text(0)
            metadata[field] = value
            parent = parent.parent()
            

        #Checking to see if there is a next tree input.  If not were at the end of the tree.
        if self.tree_inputs_layout.itemAt(column_index+1):
            #Getting the inputs for the next level of tree values
            field = self.tree_inputs_layout.itemAt(column_index+1).widget().get_tree_field()
            contains = self.tree_inputs_layout.itemAt(column_index+1).widget().get_contains_field()
            values = self.get_values(field, contains, metadata)
            for x in range(len(values)):
                child = QtWidgets.QTreeWidgetItem(it)
                child.setText(0, values[x])
                #adding an empty item as a child of this item so that it is expandable.  This will be replaced by the 
                #next level of the tree if the user clicks the expand.
                nextItem = QtWidgets.QTreeWidgetItem(child)
    def get_values(self, field, contains="", metadata={}):
        s = requests.Session()
        print(contains)
        values = s.post("https://dt4dapi.research.ge.com/api/v0/search/get/fieldValues",
                      headers={"Authorization":"Bearer " + "0003Ho7NNOnEGA27ZgvECfMnOyb8", "Content-Type" : "application/json"},
                      json = {
                            "field": field,
                            "fieldFilter": contains,
                            "group": "g01270695",
                            "metadata": metadata,
                            "startTime": self.start_date.dateTime().toMSecsSinceEpoch(),
                            "endTime": self.end_date.dateTime().toMSecsSinceEpoch()
                      })
        return values.json()

    def treeItemCollapse(self, it):
        #removing the children of the collapsed item and replacing it with an empty item so that it remains expandable.
        for i in reversed(range(it.childCount())):
            it.removeChild(it.child(i))
        nextItem = QtWidgets.QTreeWidgetItem(it)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def treeItemClick(self, it, col):
        #getting the list of values from the tree starting from the current item that was clicked before 
        #gathering values from the parents
        values = []
        values.append(it.text(col))
        parent = it.parent()
        while(parent):
            values.append(parent.text(col))
            parent = parent.parent()

        
        idx = len(values) - 1
        metadata = {}
        #getting the list of fields from the input fields corresponding to the list of values.  Iterating
        #in reverse because we got the values from the tree in reverse order.
        for x in range(len(values)):
            field = self.tree_inputs_layout.itemAt(idx).widget().get_tree_field()
            value = values[x]
            #adding the field and value to the metadata dict.
            metadata[field] = value
            idx = idx-1
        getFileRef = FSFileRef()
        getFileRef.setMetadata(metadata)
        try:
            #retrieving the list of file document sheets and calling the function to load them into the file browser table
            sheets = self.repoDriver.find(getFileRef)
            self.load_sheets(sheets)
        except Exception as ex:
            print(str(ex))

    def load_sheets(self, sheets): 
        self.sheets = sheets
        numDisplayed = min(len(sheets), 50) # Display the first 50--should be more modular for pagination
        displayedJobs = sheets[0:numDisplayed] 
        self.table.setRowCount(numDisplayed)
        #loop through the sheets provided and insert them into the file browser table
        for idx, sheet in enumerate(sheets):
            self.table.setItem(idx, 0, QTableWidgetItem(str(sheet.getName())))
            self.table.setItem(idx, 1, QTableWidgetItem(str(sheet.getId())))
            self.table.setItem(idx, 2, QTableWidgetItem(str(datetime.fromtimestamp(sheet.getTimestamp()/1000))))
            self.table.setItem(idx, 3, QTableWidgetItem(str(sheet.getSize())))
            self.table.setItem(idx, 4, QTableWidgetItem(str(sheet.getMetadata())))

    def cellClicked(self, row, column):
        #when file browser cell is clicked, we open the modal to display details of that file and provide a download button.
        DocumentModalWidget(self, self.sheets[row]).exec()

    def getRepoDriver(self):
        return self.repoDriver

    def setStyles(self):
#-------Header
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.mtv_header.sizePolicy().hasHeightForWidth())
        self.mtv_header.setSizePolicy(sizePolicy)
        self.mtv_header.setMinimumSize(QtCore.QSize(500, 54))
        self.mtv_header.setMaximumSize(QtCore.QSize(max_size, 54))
        self.mtv_header.setStyleSheet("background-color: rgb(0, 151, 255);color: rgb(255, 255, 255);font: 24pt \"Helvetica Neue\"")
        self.mtv_header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.mtv_header.setObjectName("mtv_header")
        self.mtv_header.setFont(font)
        self.mtv_header.setText("Meta Tree View")

#-------Main Page
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setObjectName("main_layout")

        self.tree_form_layout.setContentsMargins(10, 10, 10, 10)
        self.tree_form_layout.setObjectName("tree_inputs_layout")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHeightForWidth(self.scroll.sizePolicy().hasHeightForWidth())
        self.scroll.setSizePolicy(sizePolicy)
        self.scroll.setFixedHeight(300)
        self.scroll.setFixedWidth(720)
        self.scroll.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("scroll")

        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.tree_inputs_layout.setContentsMargins(0, 0, 0, 0)
        self.tree_inputs_layout.setObjectName("tree_inputs_layout")

        self.add_button.setMinimumSize(QtCore.QSize(30, 30))
        self.add_button.setMaximumSize(QtCore.QSize(30, 30))
        self.add_button.setObjectName("add_button")
        self.add_button.setStyleSheet("color:green; font-size:18px; font-weight:bold;")
        self.add_button.setText("+")

        self.mtv_tree.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.mtv_tree.setFrameShape(QtWidgets.QFrame.Shape.Panel)
        self.mtv_tree.setObjectName("mtv_tree")
        self.mtv_tree.setMaximumWidth(300)
        self.mtv_tree.setHeaderLabel("")
        self.mtv_tree.setSortingEnabled(True)
        self.mtv_tree.itemClicked.connect(self.treeItemClick)
        self.mtv_tree.itemExpanded.connect(self.treeItemExpand)
        self.mtv_tree.itemCollapsed.connect(self.treeItemCollapse)

        self.table.setGeometry(QtCore.QRect(380, 0, 401, 431))
        self.table.setObjectName("tableWidget")
        self.table.setColumnCount(5)
        self.table.horizontalHeader().setDefaultSectionSize(190)
        self.table.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels(["File Name", "ID", "Date", "File Size", "Metadata"])
        self.table.verticalHeader().setVisible(False)

#-------Footer
        self.footer.setStyleSheet("background-color: rgb(0, 151, 255);")
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.footer.setObjectName("footer")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setMaximumSize(QtCore.QSize(max_size, 54))

        self.footerLayoutWidget.setObjectName("footerLayoutWidget")

        self.btnLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.btnLayout.setContentsMargins(0, 0, 0, 0)
        self.btnLayout.setObjectName("horizontalLayout")

        self.tenant_label.setObjectName("tenant_label")
        self.tenant_label.setText("Tenant:")
        self.tenant_label.setStyleSheet("color: rgb(255, 255, 255);")

        self.tenant_selection.setObjectName("tenant_selection")
        self.tenant_selection.addItem("GroupA")
        self.tenant_selection.addItem("GroupB")
        self.tenant_selection.addItem("GroupC")
        self.tenant_selection.addItem("GroupD")
        self.tenant_selection.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tenant_selection.setMinimumSize(QtCore.QSize(150, 25))

        self.start_label.setObjectName("start_label")
        self.start_label.setText("Start:")
        self.start_label.setStyleSheet("color: rgb(255, 255, 255);")

        self.start_date.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.start_date.setCalendarPopup(True)
        self.start_date.setObjectName("start_date")
        self.start_date.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.end_label.setObjectName("end_label")
        self.end_label.setText("End:")
        self.end_label.setStyleSheet("color: rgb(255, 255, 255);")

        self.end_date.setProperty("showGroupSeparator", False)
        self.end_date.setCalendarPopup(True)
        self.end_date.setObjectName("end_date")
        self.end_date.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.submitButton.setMaximumSize(QtCore.QSize(90, 30))
        self.submitButton.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.file_browser_button.setObjectName("add_button")
        self.file_browser_button.setMaximumSize(QtCore.QSize(150, 30))
        self.file_browser_button.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.file_browser_button.setText("Choose File")

class TreeInput(QWidget):

        name = "Tree Input"
    
        def __init__(self, parent, field=None):
            super().__init__(parent)

            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(10, 10, 10, 10)

            self.tree_input_frame = QtWidgets.QWidget()
            self.treeInputWidget = QtWidgets.QWidget(self.tree_input_frame)
            self.tree_input_layout = QtWidgets.QHBoxLayout(self.treeInputWidget)

            self.removeLayout = QtWidgets.QVBoxLayout(self.treeInputWidget)
            self.removeLayout.setSpacing(0)

            self.remove_button = QtWidgets.QPushButton(self.treeInputWidget)
            self.remove_button.clicked.connect(self.remove_input)
            self.removeLayout.addWidget(self.remove_button)

            verticalSpacer = QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
            self.removeLayout.addItem(verticalSpacer)

            self.tree_input_layout.addLayout(self.removeLayout)

            self.field_layout = QtWidgets.QHBoxLayout()
            
            self.tree_field_label = QtWidgets.QLabel(self.treeInputWidget)
            self.field_layout.addWidget(self.tree_field_label)

            self.tree_field = QtWidgets.QTextEdit(self.treeInputWidget)
            self.field_layout.addWidget(self.tree_field)
            
            self.tree_input_layout.addLayout(self.field_layout)

            self.contains_layout = QtWidgets.QHBoxLayout()

            self.contains_label = QtWidgets.QLabel(self.treeInputWidget)
            self.contains_layout.addWidget(self.contains_label)

            self.contains_input = QtWidgets.QTextEdit(self.treeInputWidget)
            self.contains_layout.addWidget(self.contains_input)

            self.tree_input_layout.addLayout(self.contains_layout)

            self.setObjectName("tree_input_")

            layout.addWidget(self.tree_input_frame)

            self.setStyles(field)

            self.setLayout(layout) 

        def get_tree_field(self):
            return self.tree_field.toPlainText()

        def get_contains_field(self):
            return self.contains_input.toPlainText()

        def remove_input(self):
            self.deleteLater()

        def setStyles(self, field):
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.tree_input_frame.sizePolicy().hasHeightForWidth())
            self.tree_input_frame.setSizePolicy(sizePolicy)
            self.tree_input_frame.setObjectName("tree_input_frame")
            self.tree_input_frame.setFixedSize(QtCore.QSize(700, 90))
            self.tree_input_frame.setStyleSheet("background-color: rgb(175, 173, 176); margin: 0px 10px;")

            self.treeInputWidget.setObjectName("horizontalLayoutWidget_2")
            self.treeInputWidget.setFixedSize(QtCore.QSize(660, 70))

            self.tree_input_layout.setSpacing(0)
            self.tree_input_layout.setObjectName("tree_input_layout")

            self.remove_button.setFixedSize(QtCore.QSize(40, 20))
            self.remove_button.setStyleSheet("font-size:12px; color:white; background-color:red; border-style: hidden; border-width: 2px; border-radius: 5px;")

            self.remove_button.setText("X")

            self.tree_field.setFixedSize(QtCore.QSize(210, 30))
            self.tree_field.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.tree_field.setObjectName("tree_field")

            self.field_layout.setObjectName("field_layout")
            
            self.tree_field_label.setObjectName("tree_field_label")
            self.tree_field_label.setText("Field:")
            if field:
                self.tree_field.setText(field)

            self.contains_layout.setObjectName("contains_layout")

            self.contains_label.setObjectName("contains_label")
            self.contains_label.setText("Contains(optional):")

            self.contains_input.setFixedSize(QtCore.QSize(210, 30))
            self.contains_input.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.contains_input.setObjectName("contains_input")

            self.setFixedSize(QtCore.QSize(710, 90))

class DocumentModalWidget(QDialog):
    def __init__(self, parent, sheet):
        super().__init__(parent)
        self.sheet = sheet

        self.resize(500, 210)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        doc_info_header = QLabel("Document Details", self)
        doc_info_header.setMaximumSize(QtCore.QSize(900, 54))
        doc_info_header.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        doc_info_header.setStyleSheet("background-color: rgb(1, 26, 40);\n"
"color: rgb(255, 255, 255);\n"
"font: 24pt \"Helvetica Neue\";")
        self.layout.addWidget(doc_info_header)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setRowCount(5)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultSectionSize(450)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        item = QtWidgets.QTableWidgetItem()
        item.setText("File Name:")
        self.table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Doc ID:")
        self.table.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Date:")
        self.table.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("File Size:")
        self.table.setItem(3, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Metadata:")
        self.table.setItem(4, 0, item)
        str(sheet.getName())

        item = QtWidgets.QTableWidgetItem()
        item.setText(sheet.getName())
        self.table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(sheet.getId())
        self.table.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(str(datetime.fromtimestamp(sheet.getTimestamp()/1000)))
        self.table.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(str(sheet.getSize()))
        self.table.setItem(3, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(str(sheet.getMetadata()))
        self.table.setItem(4, 1, item)

        header = self.table.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.table)

        self.download_button = QtWidgets.QPushButton()
        print(sheet)
        self.download_button.clicked.connect(self.downloadFile)
        self.download_button.setText("Download")
        self.download_button.setMinimumWidth(100)

        self.layout.addWidget(self.layout.addWidget(self.download_button))
        
        self.setLayout(self.layout)

    def downloadFile(self):
        #opens up a file browser and downloads the file to the directory chosen.
        filePath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(self.parent().repoDriver.get(self.sheet, filePath))

