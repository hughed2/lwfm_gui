
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QTableWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QWidget, QVBoxLayout, QGraphicsTextItem, QGraphicsItem, QGraphicsPathItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath
from PyQt6.QtCore import Qt, QPointF
from graph_tool.all import *
from graph_tool.draw import sfdp_layout
import math
from lwfm.base.JobStatus import JobStatus, JobContext
from PyQt6 import QtCore, QtGui, QtWidgets

JOB_COLOR = QBrush(QColor(0, 255, 0))
PARENT_COLOR = QBrush(QColor(255, 0, 0))
ORIGIN_COLOR = QBrush(QColor(0, 0, 255))
OTHER_COLOR = QBrush(QColor(255, 255, 255))

class WorkflowGraph(QWidget):

    def __init__(self, jobs):
        super().__init__()
        self.jobs = jobs
        self.initUI()

    def initUI(self):
        # Create a Graph
        g = Graph(directed=True)

        prev_v = None
        for job in self.jobs:
            v = g.add_vertex()

            context = job.getJobContext()

            if prev_v:
                g.add_edge(prev_v, v)
            prev_v = v

        job_to_job_size = 125
        graph_width = job_to_job_size * len(jobs)
        graph_height = 150

        # Create a QGraphicsScene to hold the graph
        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, graph_width, graph_height)

        # Use graph_tool to generate the layout
        pos = sfdp_layout(g)

        # Adjust the position of the vertices to center the graph
        x_coords = [pos[v][0] for v in g.vertices()]
        y_coords = [pos[v][1] for v in g.vertices()]

        offset_x = (scene.width() - max(x_coords) - min(x_coords)) / 15
        offset_y = (scene.height() - max(y_coords) - min(y_coords)) / 2
        for v in g.vertices():
            pos[v][0] += offset_x
            pos[v][1] += offset_y
            offset_x += 120

        i = 0
        # Add the vertices to the scene
        for v in g.vertices():
            job_context = jobs[i].getJobContext()
            node_color = ORIGIN_COLOR
            if i == 0:
                node_color = ORIGIN_COLOR
            elif i == g.num_vertices() - 2:
                node_color = ORIGIN_COLOR 
            elif i == g.num_vertices() - 1:
                node_color = ORIGIN_COLOR
            item = QGraphicsEllipseItem(pos[v][0]-20, pos[v][1]-20, 40, 40)
            item.setBrush(QBrush(node_color))
            item.setPen(QPen(QColor(0, 0, 0)))
            item.label = job_context.getName()  # add label property to the node
            item.mousePressEvent = lambda event, i=i : self.node_click(jobs[i])  # add click function to the node
            scene.addItem(item)
            text_item = QGraphicsTextItem(job_context.getName())
            text_item.setPos(pos[v][0]-30, pos[v][1]-40)
            scene.addItem(text_item)
            i = i + 1
            

        # Add the edges to the scene
        for e in g.edges():
            v1 = e.source()
            v2 = e.target()
            x1, y1 = pos[v1]
            x2, y2 = pos[v2]
            dx = x2 - x1
            dy = y2 - y1
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length == 0:
                continue
            dx /= length
            dy /= length
            node_radius = 20
            x1 += dx * node_radius
            y1 += dy * node_radius
            x2 -= dx * node_radius
            y2 -= dy * node_radius
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(QPen(QColor(0, 0, 0)))
            scene.addItem(line)

            # Create a path for the arrowhead
            arrow_path = QPainterPath(QPointF(0, 0))
            arrow_path.lineTo(QPointF(-10, -5))
            arrow_path.lineTo(QPointF(-10, 5))
            arrow_path.closeSubpath()
            
            # Create a QGraphicsPathItem for the arrowhead
            arrow = QGraphicsPathItem(arrow_path)
            arrow.setPen(QPen(QColor(0, 0, 0)))
            arrow.setBrush(QBrush(QColor(0, 0, 0)))
            
            # Rotate the arrowhead to point in the right direction
            angle = math.atan2(dy, dx)
            arrow.setRotation(angle * 180 / math.pi)
            
            # Position the arrowhead at the end of the edge
            arrow.setPos(x2, y2)
            scene.addItem(arrow)

        # Create a QGraphicsView to show the scene
        view = QGraphicsView(scene)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(view)

    def node_click(self, job):
        JobStatusModalWidget(self, job).exec()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)

    jobs = []
    job1_context = JobContext()
    job1_context.setName("Launcher")
    job1_context.setOriginJobId(job1_context.getId())
    job1_context.setParentJobId("")
    job1_context.setComputeType("Local")
    job1 = JobStatus(job1_context)
    jobs.append(job1)
    job2_context = JobContext()
    job2_context.setName("Pre Processing")
    job2_context.setOriginJobId(job1_context.getId())
    job2_context.setParentJobId(job1_context.getId())
    job2_context.setComputeType("Windows")
    job2 = JobStatus(job2_context)
    jobs.append(job2)
    job3_context = JobContext()
    job3_context.setName("Notification")
    job3_context.setOriginJobId(job1_context.getId())
    job3_context.setParentJobId(job2_context.getId())
    job3_context.setComputeType("Linux")
    job3 = JobStatus(job3_context)
    jobs.append(job3)
    job4_context = JobContext()
    job4_context.setName("Simulation")
    job4 = JobStatus(job4_context)
    job4_context.setOriginJobId(job1_context.getId())
    job4_context.setParentJobId(job3_context.getId())
    job4_context.setComputeType("Windows")
    jobs.append(job4)
    job5_context = JobContext()
    job5_context.setName("Post Processing")
    job5_context.setOriginJobId(job1_context.getId())
    job5_context.setParentJobId(job4_context.getId())
    job5_context.setComputeType("Linux")
    job5 = JobStatus(job5_context)
    jobs.append(job5)
    for job in jobs:
        print(job.getJobContext().getName())

    ex = WorkflowGraph(jobs)
    ex.show()
    sys.exit(app.exec())
