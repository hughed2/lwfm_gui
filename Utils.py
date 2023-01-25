from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

def msgBox(msg, parent):
    # This opens up an alert message. It won't actually do anything, it serves only
    # as a notification.
    # "msg" is a string that will appear in the message box
    # "parent" is the QWidget producing the message box
    
    dlg = QDialog(parent)
    layout = QVBoxLayout()

    message = QLabel(msg)
    layout.addWidget(message)

    QBtn = QDialogButtonBox.StandardButton.Ok
    buttonBox = QDialogButtonBox(QBtn)
    buttonBox.accepted.connect(dlg.accept)
    layout.addWidget(buttonBox)

    dlg.setLayout(layout)
    dlg.exec()
