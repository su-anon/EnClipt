import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from view import login_register
from view import main_window
from view import preview
import controller

controller_object = controller.Controller("USER")

class LoginRegisterWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = login_register.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(400, 170)
        self.setWindowTitle("Login or Register to EnClipt")
        self.ui.register_button.clicked.connect(self.register)
        self.ui.login_button.clicked.connect(self.check_login)
        self.main_window = None

    def register(self):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        controller_object.register(username, password)

    def check_login(self):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        controller_object.login(username, password)
        if not controller_object.locked and self.main_window is None:
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.should_insert_clip = True
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("EnClipt")
        self.cliplist = controller_object.get_clipboard_list() # Get 5 most recent clips

        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clip_changed)

        self.labels = [
                self.ui.paste0,
                self.ui.paste1,
                self.ui.paste2,
                self.ui.paste3,
                self.ui.paste4
                ]
        self.btns = [
                self.ui.paste0_btn,
                self.ui.paste1_btn,
                self.ui.paste2_btn,
                self.ui.paste3_btn,
                self.ui.paste4_btn
                ]

        for i, btn in enumerate(self.btns):
            btn.clicked.connect(lambda _, index=i: self.preview(index))

        self.update_labels()
        self.ui.stack_btn_1.clicked.connect(lambda _: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.stack_btn_2.clicked.connect(lambda _: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.stack_btn_3.clicked.connect(lambda _: self.ui.stackedWidget.setCurrentIndex(2))

    def preview(self, index):
        if index<len(self.cliplist):
            text = self.cliplist[index]
            self.preview_obj = Preview(text, self)
            self.preview_obj.show()

    def clip_changed(self):
        if self.should_insert_clip == False:
            return
        clip = self.clipboard.text()
        controller_object.clip_changed(clip)
        self.cliplist = controller_object.get_clipboard_list()
        self.update_labels()

    def update_labels(self):
        for i, label in enumerate(self.labels):
            if i<len(self.cliplist):
                label.setText(self.cliplist[i])

class Preview(QtWidgets.QDialog):

    def __init__(self, text, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.clip_text = text
        self.ui = preview.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Preview")
        self.ui.preview_box.setText(self.clip_text)
        self.ui.close.clicked.connect(self.close)
        self.ui.copy.clicked.connect(self.copy_to_clip)

    def copy_to_clip(self):
        self.mainwindow.should_insert_clip = False
        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setText(self.clip_text)
        self.mainwindow.should_insert_clip = True

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginRegisterWindow()
    window.show()
    sys.exit(app.exec())

