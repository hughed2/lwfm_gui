
import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QWidget, QVBoxLayout, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt
from graph_tool.all import *
from graph_tool.draw import sfdp_layout

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a Graph
        g = Graph(directed=True)

        # Add vertices to the graph
        v1 = g.add_vertex()
        v2 = g.add_vertex()

        # Create a vertex property map for the labels
        label_prop = g.new_vertex_property("string")

        # Set the label values for each vertex
        label_prop[v1] = "Vertex 1"
        label_prop[v2] = "Vertex 2"

        print(label_prop[v1])

        e = g.add_edge(v1, v2)

        # Create a QGraphicsScene to hold the graph
        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, 400, 400)

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
            offset_x += 70

        # Add the vertices to the scene
        for v in g.vertices():
            label = label_prop[v]
            item = QGraphicsEllipseItem(pos[v][0]-20, pos[v][1]-20, 40, 40)
            item.setBrush(QBrush(QColor(255, 255, 255)))
            item.setPen(QPen(QColor(0, 0, 0)))
            item.label = label  # add label property to the node
            item.mousePressEvent = lambda event, label=label: print(label)  # add click function to the node
            scene.addItem(item)
            text_item = QGraphicsTextItem(label)
            text_item.setPos(pos[v][0]-20, pos[v][1]-40)
            scene.addItem(text_item)
            

        # Add the edges to the scene
        for e in g.edges():
            v1 = e.source()
            v2 = e.target()
            x1, y1 = pos[v1]
            x2, y2 = pos[v2]
            dx = x2 - x1
            dy = y2 - y1
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(QPen(QColor(0, 0, 0)))
            scene.addItem(line)


        # Create a QGraphicsView to show the scene
        view = QGraphicsView(scene)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(view)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphWidget()
    ex.show()
    sys.exit(app.exec())
