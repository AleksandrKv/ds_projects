import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from ui_imagedialog import Ui_Dialog

app = QApplication(sys.argv)
window = QDialog()
ui = Ui_Dialog()
ui.setupUi(window)

window.show()
msgBox = QMessageBox().critical(window, "Test title", "Some info", QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Apply | QMessageBox.StandardButton.Cancel)

print (msgBox)


sys.exit(app.exec())

