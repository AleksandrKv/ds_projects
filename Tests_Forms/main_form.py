import pickle
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication

Form, Window = uic.loadUiType("Tests_Forms\MainForm.ui")

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

def on_click_Bunnton_1():
    ls = [1,2,3,"dfjfalwjef",44]

    file1 = open("config.txt", "wb")
    pickle.dump(ls, file1)
    file1.close()
    print("File saved!")

def on_click_Bunnton_2():

    file1 = open("config.txt", "rb")
    ob = pickle.load(file1)
    file1.close()
    print(ob)

form.pushButton_1.clicked.connect(on_click_Bunnton_1)
form.pushButton_2.clicked.connect(on_click_Bunnton_2)

window.show()


app.exec()


