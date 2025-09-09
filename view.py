import sys, threading, os
from PyQt6 import QtWidgets, QtCore, QtGui
from view import register, login, main_window, preview, fileoperation
import controller

controller_object = controller.Controller()

class Register(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = register.Ui_Form()
        self.ui.setupUi(self)
        self.setFixedSize(233, 363)
        self.setWindowTitle("Register")
        self.ui.keyfile.clicked.connect(self.keyfile_func)
        self.ui.register_button.clicked.connect(self.register_func)
        self.keyfile_path = None
        self.setup_authenticator()

    def setup_authenticator(self):
        buffer = controller_object.get_authenticator_secret()
        self.ui.authenticator.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(buffer)))

    def register_func(self):
        if not self.keyfile_path:
            QtWidgets.QMessageBox.critical(self, "Error", "Please select a key file path.")
            return
        try:
            with open(self.keyfile_path, 'wb') as f:
                f.write(controller_object.getkeyfile())
            password = self.ui.master_password.text()
            controller_object.register(password)
            self.login = Login()
            self.close()
            self.login.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save key file: {str(e)}")

    def keyfile_func(self):
        self.keyfile_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Key File", "enclipt.key", "Key Files (*.key);;All Files (*)"
        )
        if self.keyfile_path:
            self.show_toast("Key file path selected")
        else:
            self.show_toast("No key file path selected")

    def show_toast(self, message):
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
        custom_center = self.rect().center()
        toast_center = toast.rect().center()
        toast.move(custom_center - toast_center)
        toast.show()
        toast.raise_()
        QtCore.QTimer.singleShot(1000, toast.hide)

class Login(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = login.Ui_Form()
        self.ui.setupUi(self)
        self.setFixedSize(334, 143)
        self.setWindowTitle("Login")
        self.ui.login_button.clicked.connect(self.handle_login2)
        self.ui.keyfile.clicked.connect(self.get_keyfile_path)
        self.keyfile_path = None
        self.keyfile_valid = False
        self.totp_valid = False
        self.password_valid = False

    def handle_login2(self):
        self.totp_validation()
        self.password_validation()
        if not self.keyfile_path:
            self.keyfile_valid = False
        else:
            self.keyfile_validation()
        if self.keyfile_valid and self.totp_valid and self.password_valid:
            self.show_toast("Login successful")
            self.main_window = MainWindow()
            self.close()
            self.main_window.show()
        else:
            self.show_toast("Login failed: Invalid credentials")

    def get_keyfile_path(self):
        self.keyfile_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Key File", "", "Key Files (*.key);;All Files (*)"
        )
        if self.keyfile_path:
            self.show_toast("Key file selected")
            self.keyfile_validation()
        else:
            self.show_toast("No key file selected")
            self.keyfile_valid = False

    def keyfile_validation(self):
        try:
            with open(self.keyfile_path, 'rb') as f:
                key = f.read()
            if not key:
                self.show_toast("Key file is empty")
                self.keyfile_valid = False
                return
            self.keyfile_valid = controller_object.authenticate_keyfile(key)
            if not self.keyfile_valid:
                self.show_toast("Invalid key file")
        except Exception as e:
            self.show_toast(f"Error reading key file: {str(e)}")
            self.keyfile_valid = False

    def totp_validation(self):
        self.totp_valid = controller_object.authenticate_totp(self.ui.otp.text())

    def password_validation(self):
        self.password_valid = controller_object.is_password_correct(self.ui.password.text())

    def show_toast(self, message):
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
        custom_center = self.rect().center()
        toast_center = toast.rect().center()
        toast.move(custom_center - toast_center)
        toast.show()
        toast.raise_()
        QtCore.QTimer.singleShot(1000, toast.hide)

class FileOperation(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedSize(620,143)
        self.ui = fileoperation.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("Backup/Restore Database")
        self.ui.backup.clicked.connect(self.select_backup_path)
        self.ui.restore.clicked.connect(self.select_restore_path)
        self.ui.confirm.clicked.connect(self.confirm_operation)
        self.operation = None
        self.file_path = None

    def select_backup_path(self):
        self.file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Backup Database", "enclipt_backup.db", "Database Files (*.db);;All Files (*)"
        )
        if self.file_path:
            self.ui.file_status.setText(f"Backup path: {self.file_path}")
            self.operation = 'backup'
        else:
            self.ui.file_status.setText("No backup path selected")
            self.operation = None

    def select_restore_path(self):
        self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Backup Database", "", "Database Files (*.db);;All Files (*)"
        )
        if self.file_path:
            self.ui.file_status.setText(f"Restore path: {self.file_path}")
            self.operation = 'restore'
        else:
            self.ui.file_status.setText("No restore path selected")
            self.operation = None

    def confirm_operation(self):
        password = self.ui.file_password.text()
        if not password:
            self.ui.file_status.setText("No password provided")
            return
        if not self.file_path or not self.operation:
            self.ui.file_status.setText("Select a file path first")
            return
        if self.operation == 'backup':
            success, message = controller_object.backup_database(self.file_path, password)
            self.ui.file_status.setText(message)
        elif self.operation == 'restore':
            success, message = controller_object.restore_database(self.file_path, password)
            self.ui.file_status.setText(message)
            if success:
                self.main_window.cliplist = controller_object.get_clipboard_list(state=1)
                self.main_window.update_labels()
                self.close()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.should_insert_clip = True
        self.cliptimeout = -1
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("EnClipt")
        self.cliplist = controller_object.get_clipboard_list(state=1)
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
        self.ui.stack_btn_prev.clicked.connect(self.prev_page)
        self.ui.stack_btn_next.clicked.connect(self.next_page)
        self.ui.stack_btn_1.clicked.connect(lambda _: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.stack_btn_2.clicked.connect(lambda _: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.stack_btn_3.clicked.connect(lambda _: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.stack_btn_4.clicked.connect(self.open_file_operation)
        self.page_label = QtWidgets.QLabel(self.ui.centralwidget)
        self.page_label.setStyleSheet("font-size: 16px;")
        self.page_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ui.verticalLayout.addWidget(self.page_label)
        self.update_labels()

    def open_file_operation(self):
        self.file_op_window = FileOperation(self)
        self.file_op_window.show()

    def next_page(self):
        prev_offset = controller_object.model.offset
        self.cliplist = controller_object.get_clipboard_list(state=2)
        self.update_labels()
        if len(self.cliplist) < 5 and self.cliplist and controller_object.model.offset == prev_offset:
            self.show_toast("No more clips available", self.ui.centralwidget)

    def prev_page(self):
        self.cliplist = controller_object.get_clipboard_list(state=3)
        self.update_labels()

    def preview(self, index):
        if index < len(self.cliplist):
            text = self.cliplist[index]
            self.preview_obj = Preview(text, self)
            self.preview_obj.show()

    def clip_changed(self):
        if not self.should_insert_clip:
            return
        clip = self.clipboard.text()
        if not clip:
            return
        if controller_object.clip_changed(clip):
            self.cliplist = controller_object.get_clipboard_list(state=1)
            self.update_labels()
            if self.cliptimeout >= 0:
                if self.clear_timer.isActive():
                    self.clear_timer.stop()
                self.clear_timer.start(self.cliptimeout)
        else:
            self.show_toast("Duplicate clip not added", self.ui.centralwidget)

    def update_labels(self):
        for i, label in enumerate(self.labels):
            label.setText(self.cliplist[i] if i < len(self.cliplist) else "󰛌 Empty Paste!")
        self.ui.stack_btn_prev.setEnabled(controller_object.model.offset > 0)
        self.ui.stack_btn_next.setEnabled(len(self.cliplist) == 5)
        page_num = (controller_object.model.offset // 5) + 1
        self.page_label.setText(f"Page {page_num}")

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
            self.show_toast(f"Set to lock after {timeout} second(s)", self.ui.lock_timer_widget)
            if self.locker_timer.isActive():
                self.locker_timer.stop()
            self.locker_timer.start(int(timeout) * 1000)
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
