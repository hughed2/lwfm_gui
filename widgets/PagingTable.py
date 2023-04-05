import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QAbstractItemView, QHBoxLayout, QWidget, QPushButton, QHeaderView, QVBoxLayout, QLabel, QComboBox

class Table(QWidget):
    def __init__(self, data, items_per_page):
        super().__init__()

        self.data = data
        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_pages = len(self.data) // self.items_per_page + 1

        # Pagination buttons
        self.prev_button = QPushButton("Prev")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)

        # Page numbers label
        self.page_label = QLabel(f"Page {self.current_page} of {self.total_pages}")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Rows per page combobox
        self.rows_per_page_combobox = QComboBox()
        self.rows_per_page_combobox.addItems(["10", "20", "50"])
        self.rows_per_page_combobox.setCurrentText(str(self.items_per_page))
        self.rows_per_page_combobox.currentTextChanged.connect(self.change_items_per_page)

        self.init_ui()

    def init_ui(self):
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Name", "Age"])

        self.update_table()

        hbox = QHBoxLayout()
        hbox.addWidget(self.prev_button)
        hbox.addWidget(self.page_label)
        hbox.addWidget(self.next_button)
        hbox.addWidget(QLabel("Rows per page:"))
        hbox.addWidget(self.rows_per_page_combobox)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.table)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def update_table(self):
        self.table.clearContents()
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = min(start_index + self.items_per_page, len(self.data))
        self.table.setRowCount(end_index - start_index)

        for row_index, row_data in enumerate(self.data[start_index:end_index]):
            for column_index, cell_data in enumerate(row_data):
                cell = QTableWidgetItem(str(cell_data))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_index, column_index, cell)

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        # Update page label
        self.total_pages = len(self.data) // self.items_per_page + 1
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_table()

    def change_items_per_page(self, items_per_page):
        self.items_per_page = int(items_per_page)
        self.current_page = 1
        self.update_table()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    data = [
        ["Alice", 20],
        ["Bob", 25],
        ["Charlie", 30],
        ["Dave", 35],
        ["Eve", 40],
        ["Frank", 45],
        ["Grace", 50],
        ["Henry", 55],
        ["Ivy", 60],
        ["Jack", 65],
        ["Karen", 70],
        ["Larry", 75],
        ["Maggie", 80],
        ["Nancy", 85],
        ["Oscar", 90],
        ["Paul", 95],
        ["Queenie", 100],
        ["Robert", 105],
        ["Sarah", 110],
        ["Tom", 115],
        ["Ursula", 120],
        ["Victor", 125],
        ["Wendy", 130],
        ["Xander", 135],
        ["Yara", 140],
        ["Zoe", 145]
    ]

    items_per_page = 10
    table = Table(data, items_per_page)
    table.show()

    sys.exit(app.exec())