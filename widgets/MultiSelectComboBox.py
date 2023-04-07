from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QComboBox, QListView

class MultiSelectComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Connects the 'pressed' signal of the view
        self.view().pressed.connect(self.handle_item_pressed)
        self.model = QStandardItemModel(self)
        self.setModel(self.model)
        # Stores the check state of each item in the ComboBox
        self.check_states = []

    def handle_item_pressed(self, index):
        item = self.model.itemFromIndex(index)
        # Toggles the check state of the item
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        self.update_check_states()

    def addItem(self, item):
        standard_item = QStandardItem(item)
        standard_item.setCheckable(True)
        standard_item.setCheckState(Qt.CheckState.Unchecked)
        self.model.appendRow(standard_item)
        self.check_states.append(False)
        # If this is the first item added, set the current text to the items text
        if self.model.rowCount() == 1:
            self.setCurrentText(item)
        self.update_check_states()

    def update_check_states(self):
        # Updates the check state of each item in the ComboBox
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            self.check_states[index] = item.checkState() == Qt.CheckState.Checked
            item.setCheckState(Qt.CheckState.Checked if self.check_states[index] else Qt.CheckState.Unchecked)

    def showPopup(self):
        self.update_check_states()
        super().showPopup()

    def checkedItems(self, clear=True):
        # Returns a list of all items that are currently checked
        items = []
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                items.append(item.text())
        if clear:
            self.check_states = [item.checkState() == Qt.CheckState.Checked for item in self.model]
        return items
