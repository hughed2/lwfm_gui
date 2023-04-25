import sys
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt6.QtWidgets import QApplication

from PyQt6 import QtCore, QtGui, QtWidgets

from widgets.WorkflowGraph import WorkflowGraph

class GraphWidget(QWidget):
    name = "Trigger List"
    
    def __init__(self, parent):
        super().__init__(parent)

        self.get_jobs()

        self.initUI()

    def initUI(self):

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
        self.header.setText(_translate("MainWindow", "Graph"))

        layout.addWidget(self.header)

        self.scroll = QScrollArea(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHeightForWidth(self.scroll.sizePolicy().hasHeightForWidth())
        self.scroll.setSizePolicy(sizePolicy)
        self.scroll.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scroll.setWidgetResizable(True)
        self.scroll.setProperty("class", "scroll")
        self.scroll.setFixedWidth(800)
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidget.setProperty("class", "scrollWidget")

        self.workflow = WorkflowGraph(self.jobs)
        self.scroll.addWidget(self.workflow)

        self.footer = QtWidgets.QFrame()
        self.footer.setProperty("class", "footer")
        self.footer.setGeometry(QtCore.QRect(0, 530, 741, 61))
        self.footer.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.footer.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)

        layout.addWidget(self.footer)

        self.setLayout(layout)        

        self.show()

    def get_jobs(self):
        self.jobs = []
        job1_context = JobContext()
        job1_context.setName("Launcher")
        job1_context.setOriginJobId(job1_context.getId())
        job1_context.setParentJobId("")
        job1_context.setComputeType("Local")
        job1 = self.jobstatus(job1_context)
        self.jobs.append(job1)
        job2_context = JobContext()
        job2_context.setName("Pre Processing")
        job2_context.setOriginJobId(job1_context.getId())
        job2_context.setParentJobId(job1_context.getId())
        job2_context.setComputeType("Windows")
        job2 = self.jobstatus(job2_context)
        self.jobs.append(job2)
        job3_context = JobContext()
        job3_context.setName("Notification")
        job3_context.setOriginJobId(job1_context.getId())
        job3_context.setParentJobId(job2_context.getId())
        job3_context.setComputeType("Linux")
        job3 = self.jobstatus(job3_context)
        self.jobs.append(job3)
        job4_context = JobContext()
        job4_context.setName("Simulation")
        job4 = self.jobstatus(job4_context)
        job4_context.setOriginJobId(job1_context.getId())
        job4_context.setParentJobId(job3_context.getId())
        job4_context.setComputeType("Windows")
        self.jobs.append(job4)
        job5_context = JobContext()
        job5_context.setName("Post Processing")
        job5_context.setOriginJobId(job1_context.getId())
        job5_context.setParentJobId(job4_context.getId())
        job5_context.setComputeType("Linux")
        job5 = self.jobstatus(job5_context)
        self.jobs.append(job5)