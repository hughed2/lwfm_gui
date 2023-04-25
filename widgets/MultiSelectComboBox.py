
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QComboBox, QListView, QApplication, QMainWindow
from PyQt6 import QtCore

class MultiSelectComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Connects the 'pressed' signal of the view
        self.view().pressed.connect(self.handle_item_pressed)
        self.model = QStandardItemModel(self)
        self.setModel(self.model)
        # Stores the check state of each item in the ComboBox
        self.check_states = []
        combo_box_rect = self.geometry()

        # Get the current popup widget
        popup_widget = self.view()

        # Calculate the new position of the popup widget
        new_x = combo_box_rect.left()
        new_y = combo_box_rect.bottom() + 20

        # Set the new position of the popup widget
        popup_widget.move(new_x, new_y)

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

class ExampleMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        combo_box = MultiSelectComboBox(self)
        combo_box.setStyleSheet(
            '''
                /* Set the height and width of the QComboBox */
                QComboBox {
                height: 25px;
                padding: 2px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
                selection-background-color: #e5eaF8;
                }

                /* Set the background color and border radius of the dropdown button */
                QComboBox::drop-down {
                image: url(icons/down.png);
                min-width: 25px;
                min-height: 25px;
                background-color: #f8f9fa;
                border: 1px solid #ccc;
                border-radius: 5px;
                }

                /* Set the background color and border radius of the dropdown list */
                QComboBox::drop-down::menu {
                background-color: #f8f9fa;
                border: 1px solid #ccc;
                border-radius: 5px;
                }

                /* Set the color of the items in the dropdown list */
                QComboBox::item {
                color: #212529;
                }

                /* Set the background color of the selected item in the dropdown list */
                QComboBox::item:selected {
                background-color: #e5eaF8;
                }

                /* Set the color of the arrow icon */
                QComboBox::down-arrow {
                image: url(icons/down.png);
                color: black;
                }
            '''
        )

        combo_box.addItem("Item 1")
        combo_box.addItem("Item 2")
        combo_box.addItem("Item 3")

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExampleMainWindow()
    sys.exit(app.exec())
