
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QComboBox, QListView

class MultiSelectComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view().pressed.connect(self.handle_item_pressed)
        self.model = QStandardItemModel(self)
        self.setModel(self.model)

    def handle_item_pressed(self, index):
        item = self.model.itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    def addItem(self, item):
        standard_item = QStandardItem(item)
        standard_item.setCheckable(True)
        standard_item.setCheckState(Qt.CheckState.Unchecked)
        self.model.appendRow(standard_item)
        if self.model.rowCount() == 1:
            self.setCurrentText(item)

    def checkedItems(self):
        items = []
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                items.append(item.text())
        return items
