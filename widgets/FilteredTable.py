
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QRegularExpression, pyqtSignal, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPalette, QColor, QBrush
from PyQt6.QtWidgets import QApplication, QTableView, QLineEdit, QVBoxLayout, QWidget, QAbstractItemView

class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_regexes = {}

    def setFilterRegex(self, column, regex):
        self._filter_regexes[column] = regex
        self.invalidateFilter()

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

    def lessThan(self, left, right):
        if left.row() == 0 or right.row() == 0:
            return False  # Don't sort the first row (header row)
        return super().lessThan(left, right)


class FilterWidget(QWidget):
    def __init__(self, view, parent=None):
        super().__init__(parent)
        self._view = view
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
            self._view.setIndexWidget(self._view.model().index(0, i), line_edit)

    def _on_text_changed(self, text):
        sender = self.sender()
        column = self._filters.index(sender)
        proxy_model = self._view.model()
        regex = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        proxy_model.setFilterRegex(column, regex)

class FilteredTable(QWidget):
    rowClicked = pyqtSignal(int)

    def __init__(self, data, headers, parent=None):
        super().__init__(parent)
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
        self.filter_widget = FilterWidget(self.table_view, self)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.addWidget(filter_widget)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

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

    def update_data(self, data):
        print("Updating data...")
        for line_edit in self.filter_widget._filters:
            line_edit.textChanged.disconnect(self.filter_widget._on_text_changed)
            line_edit.clear()
            line_edit.textChanged.connect(self.filter_widget._on_text_changed)
        model = self.table_model.sourceModel()
        model.removeRows(1, model.rowCount() - 1)
        for row in data:
            items = [QStandardItem(str(field)) for field in row]
            model.appendRow(items)
        self.table_model.invalidateFilter()

    def update_headers(self, headers):
        model = self.table_model.sourceModel()
        model.setHorizontalHeaderLabels(headers)

if __name__ == '__main__':
    app = QApplication([])
    data = [[1, "apple", "red"], [2, "banana", "yellow"], [3, "orange", "orange"], [4, "kiwi", "green"]]
    headers = ["ID", "Fruit", "Color"]
    window = FilteredTable(data, headers)
    window.rowClicked.connect(lambda row: print(f"Row clicked: {row}"))
    window.show()
    new_data = [[5, "grape", "purple", "test"], [6, "watermelon", "green", "Test"], [7, "peach", "orange", "tst"]]
    QTimer.singleShot(5000, lambda: window.update_data(new_data))
    QTimer.singleShot(5000, lambda: window.update_headers(["ID", "Fruit", "Color"]))
    app.exec()
