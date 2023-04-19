
import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QWidget, QVBoxLayout, QGraphicsTextItem, QGraphicsItem, QGraphicsPathItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath
from PyQt6.QtCore import Qt, QPointF
from graph_tool.all import *
from graph_tool.draw import sfdp_layout
import math

class GraphWidget(QWidget):
    def __init__(self, jobs):
        super().__init__()
        self.initUI()
        self.jobs = jobs

    def initUI(self):
        # Create a Graph
        g = Graph(directed=True)

        # Add vertices to the graph
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()

        # Create a vertex property map for the labels
        job_name = g.new_vertex_property("string")
        job_id = g.new_vertex_property("string")

        # Set the job name values for each vertex
        job_name[v1] = "Launcher"
        job_name[v2] = "Pre Processing"
        job_name[v3] = "Simulation"
        job_name[v4] = "Post Processing"

        # Set the job name values for each vertex
        job_id[v1] = "asdjflas"
        job_id[v2] = "piodjhfe"
        job_id[v3] = "eidnafan"
        job_id[v4] = "qmdhadsf"

        g.add_edge(v1, v2)
        g.add_edge(v2, v3)
        g.add_edge(v3, v4)

        # Create a QGraphicsScene to hold the graph
        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, 500, 100)

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
            name = job_name[v]
            node_color = QBrush(QColor(255, 255, 255))
            if i == 0:
                node_color = QBrush(QColor(0, 0, 255))
            elif i == 2:
                node_color = QBrush(QColor(255, 0, 0)) 
            elif i == 3:
                node_color = QBrush(QColor(0, 255, 0))
            jid = job_id[v]
            item = QGraphicsEllipseItem(pos[v][0]-20, pos[v][1]-20, 40, 40)
            item.setBrush(QBrush(node_color))
            item.setPen(QPen(QColor(0, 0, 0)))
            item.label = name  # add label property to the node
            item.mousePressEvent = lambda event, name=name, jid=jid : self.node_click(name, jid)  # add click function to the node
            scene.addItem(item)
            text_item = QGraphicsTextItem(name)
            text_item.setPos(pos[v][0]-20, pos[v][1]-40)
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

    def node_click(self, job_name, job_id):
        print ("Job Name: " + job_name + ", ID:" + job_id)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphWidget()
    ex.show()
    sys.exit(app.exec())
