import sys, threading, os
from PyQt6 import QtWidgets, QtCore, QtGui
from view import register, login, main_window, preview
import controller

controller_object = controller.Controller()

# class LoginRegisterWindow(QtWidgets.QMainWindow):
# 
#     def __init__(self):
#         super().__init__()
#         self.ui = login_register.Ui_MainWindow()
#         self.ui.setupUi(self)
#         self.setFixedSize(400, 170)
#         self.setWindowTitle("Login or Register to EnClipt")
#         self.ui.register_button.clicked.connect(self.register)
#         self.ui.login_button.clicked.connect(self.check_login)
#         self.main_window = None
# 
#     def register(self):
#         username = self.ui.username_input.text()
#         password = self.ui.password_input.text()
#         controller_object.register(username, password)
# 
#     def check_login(self):
#         username = self.ui.username_input.text()
#         password = self.ui.password_input.text()
#         controller_object.login(username, password)
#         if not controller_object.locked and self.main_window is None:
#             self.main_window = MainWindow()
#             self.main_window.show()
#             self.close()
#             del(self)

class Register(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = register.Ui_Form()
        self.ui.setupUi(self)
        self.setFixedSize(233, 363)
        self.setWindowTitle("Register")
        self.ui.keyfile.clicked.connect(self.keyfile_func)
        self.ui.register_button.clicked.connect(self.register_func)
        self.keyfile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "keyfile")

    def register_func(self):
        with open(self.keyfile_path, 'wb') as f:
            f.write(controller_object.getkeyfile())
        print('Regiseter')
    def keyfile_func(self):
        self.keyfile_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Key File", "enclipt.key", "Key Files (*.key);;All Files (*)")

class Login(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui  = login.Ui_Form()
        self.ui.setupUi(self)
        self.setFixedSize(334, 143)
        self.setWindowTitle("Login")
        self.ui.login_button.clicked.connect(self.handle_login)
        self.ui.keyfile.clicked.connect(self.keyfile_validation)
        self.keyfile_valid = False

    def handle_login(self):
        pass

    def keyfile_validation(self):
        self.keyfile_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Save Key File", "", "Key Files (*.key);;All Files (*)")
        with open(self.keyfile_path, 'rb') as f:
            key = f.read()
        self.keyfile_valid = controller_object.authenticate_keyfile(key)
        print(self.keyfile_valid)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.should_insert_clip = True
        self.cliptimeout = -1
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("EnClipt")
        self.cliplist = controller_object.get_clipboard_list(forward=True) # Get 5 most recent clips

        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clip_changed)

        self.clear_timer = QtCore.QTimer()
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.clipboard.clear)

        self.locker_timer = QtCore.QTimer()
        self.locker_timer.setSingleShot(True)
        self.locker_timer.timeout.connect(self.lock_function)


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
        self.ui.clip_timer_btn.clicked.connect(self.clip_timer)
        self.ui.lock_timer_btn.clicked.connect(self.lock_timer)

    def preview(self, index):
        if index<len(self.cliplist):
            text = self.cliplist[index]
            self.preview_obj = Preview(text, self)
            self.preview_obj.show()

    def clip_changed(self):
        if self.should_insert_clip == False:
            return
        clip = self.clipboard.text()
        if not clip:
            return
        controller_object.clip_changed(clip)
        self.cliplist = controller_object.get_clipboard_list()
        self.update_labels()

        if self.cliptimeout >= 0:
            if self.clear_timer.isActive():
                self.clear_timer.stop()
            self.clear_timer.start(self.cliptimeout)

    def update_labels(self):
        for i, label in enumerate(self.labels):
            if i<len(self.cliplist):
                label.setText(self.cliplist[i])

    def show_toast(self, message, widget):
        toast = QtWidgets.QLabel(message, self)
        toast.setStyleSheet("""
            background-color: #333;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        """)
        toast.setWordWrap(True)
        toast.setFixedWidth(200)
        toast.adjustSize()
        toast.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        custom_center = widget.mapTo(self, widget.rect().center())
        toast_center = toast.rect().center()
        toast.move(custom_center - toast_center)
        
        toast.show()
        toast.raise_()
        QtCore.QTimer.singleShot(1000, toast.hide)

    def clip_timer(self):
        timeout = self.ui.clip_timer_input.text()
        if self.is_valid_time(timeout):
            self.cliptimeout = int(timeout) * 1000
            self.show_toast(f"Set to clear clipboard after {timeout} second(s)", self.ui.clipboard_timer_widget)
            self.clear_timer.start(self.cliptimeout)
        else:
            self.show_toast("Enter valid time", self.ui.clipboard_timer_widget)
    
    def lock_timer(self):
        timeout = self.ui.lock_timer_input.text()
        if self.is_valid_time(timeout):
            self.show_toast(f"Set to lock after {timeout} second", self.ui.lock_timer_widget)
            if self.locker_timer.isActive():
                self.locker_timer.stop()
            self.locker_timer.start(int(timeout)*1000)
        else:
            self.show_toast("Enter valid time", self.ui.lock_timer_widget)

    def lock_function(self):
        self.login_window = Login()
        self.login_window.show()
        self.close()

    def is_valid_time(self, text):
        try:
            int(text)
            return True
        except:
            return False


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

    db_path = "model/database"

    if not os.path.exists(db_path):
        window = Register()
    else:
        window = Login()

    window.show()
    sys.exit(app.exec())
