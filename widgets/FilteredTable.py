

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QRegularExpression, pyqtSignal, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPalette, QColor, QBrush, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QTableView, QLineEdit, QVBoxLayout, QWidget, QAbstractItemView, QHBoxLayout, QPushButton, QHeaderView, QLabel, QComboBox, QSpacerItem
from PyQt6 import QtWidgets

# custom QSortFilterProxyModel for filtering the table data
class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_regexes = {}

    # set the filter regex for a given column
    def setFilterRegex(self, column, regex):
        self._filter_regexes[column] = regex
        self.invalidateFilter()

    # check if a row matches all the filter regexes
    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        if sourceRow == 0:
            return True

        for column in self._filter_regexes:
            if self.sourceModel().data(self.sourceModel().index(sourceRow, column)):
                text = self.sourceModel().data(self.sourceModel().index(sourceRow, column)).lower()
                regex = self._filter_regexes[column]
                if regex.pattern().lower() not in text:
                    return False
        return True

    # don't sort the first row (header row)
    def lessThan(self, left, right):
        if left.row() == 0 or right.row() == 0:
            return False
        return super().lessThan(left, right)


class FilterWidget(QWidget):
    def __init__(self, view, view_copy, parent=None):
        super().__init__(parent)
        self._view = view
        self._view_copy = view_copy
        self._filters = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        # items = [QStandardItem() for _ in range(self._view.model().columnCount())]
        # self._view.model().sourceModel().appendRow(items)

        for i in range(self._view.model().columnCount()):
            line_edit = QLineEdit(self)
            line_edit.setPlaceholderText("Filter...")
            line_edit.textChanged.connect(self._on_text_changed)
            self._filters.append(line_edit)
            layout.addWidget(line_edit)
            # set the filter input box as the index widget for the corresponding column header
            self._view.setIndexWidget(self._view.model().index(0, i), line_edit)

    # update the filter regex for a column when its input box is changed
    def _on_text_changed(self, text):
        sender = self.sender()
        column = self._filters.index(sender)
        proxy_model = self._view_copy.model()
        regex = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        proxy_model.setFilterRegex(column, regex)

        sender = self.sender()
        column = self._filters.index(sender)
        proxy_model = self._view_copy.model()
        regex = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        proxy_model.setFilterRegex(column, regex)
        # create a delay on the filtering so that it won't filter until the user is done typing
        self._view = self._view_copy
        QTimer.singleShot(5000, self._view.viewport().update)

# custom widget that contains the filtered table
class FilteredTable(QWidget):
    # signal emitted when a row in the table is clicked
    rowClicked = pyqtSignal(int)

    def __init__(self, data, headers, parent=None):
        super().__init__(parent)
        self.data = data
        # create the table model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        item = QStandardItem()
        item.setFlags(Qt.ItemFlag(0)) 
        model.appendRow(item)
        for row in data:
            items = [QStandardItem(str(field)) for field in row]
            model.appendRow(items)
        self.table_model = FilterModel()
        self.table_model.setSourceModel(model)
        self.table_view = QTableView(self)
        self.table_view.setSortingEnabled(True)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_view.setAlternatingRowColors(True)

        self.table_view_copy = self.table_view

        palette = QPalette()
        brush = QBrush(QColor(229, 234, 248))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush)
        brush = QBrush(QColor(229, 234, 248))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush)
        brush = QBrush(QColor(229, 234, 248))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush)
        self.table_view.setPalette(palette)
        self.table_view.setModel(self.table_model)
        self.table_view.clicked.connect(self._on_row_clicked)

        self.items_per_page = 3
        self.current_page = 1
        self.total_pages = len(data) // self.items_per_page + 1

        previous_icon = QIcon(QPixmap("icons/left-arrow.png"))
        next_icon = QIcon(QPixmap("icons/right-arrow.png"))

        # Pagination buttons
        self.prev_button = QPushButton()
        self.prev_button.setIcon(previous_icon)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button = QPushButton()
        self.next_button.setIcon(next_icon)
        self.next_button.clicked.connect(self.next_page)

        # Page numbers label
        self.page_label = QLabel(f"Page {self.current_page} of {self.total_pages}")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Rows per page combobox
        self.rows_per_page_combobox = QComboBox()
        self.rows_per_page_combobox.addItems(["3", "10", "20", "50"])
        self.rows_per_page_combobox.setCurrentText(str(self.items_per_page))
        self.rows_per_page_combobox.currentTextChanged.connect(self.change_items_per_page)

        self.filter_widget = FilterWidget(self.table_view, self.table_view_copy, self)

        hbox = QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addWidget(self.prev_button)
        hbox.addWidget(self.page_label)
        hbox.addWidget(self.next_button)
        hbox.addWidget(QLabel("Rows per page:"))
        hbox.addWidget(self.rows_per_page_combobox)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spacerItem = QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        #hbox.addItem(spacerItem)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.addWidget(filter_widget)
        layout.addWidget(self.table_view)
        layout.addLayout(hbox)
        self.setLayout(layout)

    # emit a signal when a row is clicked in the table view
    def _on_row_clicked(self, index):
        source_index = self.table_model.mapToSource(index)
        row = source_index.row() - 1
        self.rowClicked.emit(row)

    def get_table_view(self):
        return self.table_view

    def set_table_view(self, table_view):
        self.table_view = table_view

    def get_table_model(self):
        return self.table_model

    def set_table_model(self, table_model):
        self.table_model = table_model

    #Updates the data in the table with new data and updates the filters and table view accordingly.
    def update_data(self, data):
        self.data = data
        # Disconnect textChanged signal from each filter QLineEdit to avoid updating filters when clearing them
        for line_edit in self.filter_widget._filters:
            line_edit.textChanged.disconnect(self.filter_widget._on_text_changed)
            line_edit.clear()
            line_edit.textChanged.connect(self.filter_widget._on_text_changed)
        # Update table model with new data
        model = self.table_model.sourceModel()
        model.removeRows(1, model.rowCount() - 1)
        for row in data:
            items = [QStandardItem(str(field)) for field in row]
            model.appendRow(items)
        self.table_model.invalidateFilter()
        self.update_table()

    #Updates the headers of the table with new headers.
    def update_headers(self, headers):
        model = self.table_model.sourceModel()
        model.setHorizontalHeaderLabels(headers)

    #Updates the table view with the current data, headers, and pagination settings.
    def update_table(self):
        model = self.table_model.sourceModel()

        # Calculate the start and end index of the data to display based on the current page and items per page settings
        start_index = (self.current_page - 1) * self.items_per_page
        if model.rowCount() > 1:
            model.removeRows(1, model.rowCount())
            end_index = min(start_index + self.items_per_page, len(self.data))
        else:
            end_index = min(start_index + self.items_per_page, 1)

        # Set the row count of the table model to the number of rows to display
        model.setRowCount(end_index - start_index)

        # Iterate over the data to display and set the cell values in the table model
        for row_index, row_data in enumerate(self.data[start_index:end_index]):
            for column_index, cell_data in enumerate(row_data):
                cell = QStandardItem(str(cell_data))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                model.setItem(row_index+1, column_index, cell)

        # Update the total number of pages and the page label
        self.total_pages = (len(self.data) - 1) // self.items_per_page + 1
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")

    #Moves the table view to the previous page of data if possible.
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table()

    #Moves the table view to the next page of data if possible.
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_table()

    #Changes the number of items to display per page and updates the table view accordingly.
    def change_items_per_page(self, items_per_page):
        self.items_per_page = int(items_per_page)
        self.current_page = 1
        self.update_table()

if __name__ == '__main__':
    app = QApplication([])
    data = [[1, "apple", "red"], [2, "banana", "yellow"], [3, "orange", "orange"], [4, "kiwi", "green"], [1, "apple", "red"], [2, "banana", "yellow"], [3, "orange", "orange"], [4, "kiwi", "green"],[1, "apple", "red"], [2, "banana", "yellow"], [3, "orange", "orange"], [4, "kiwi", "green"],[1, "apple", "red"], [2, "banana", "yellow"], [3, "orange", "orange"], [4, "kiwi", "green"],[1, "apple", "red"], [2, "banana", "yellow"], [3, "orange", "orange"], [4, "kiwi", "green"],[1, "apple", "red"], [2, "banana", "yellow"], [3, "orange", "orange"], [4, "kiwi", "green"],]
    headers = ["ID", "Fruit", "Color"]
    window = FilteredTable(data, headers)
    window.rowClicked.connect(lambda row: print(f"Row clicked: {row}"))
    window.show()
    new_data = [[5, "grape", "purple", "test"], [6, "watermelon", "green", "Test"], [7, "peach", "orange", "tst"]]
    app.exec()
