"""Основной файл приложения"""
import os
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow

from functions import center, user_size
from login import Login_window
from registration import Reg_window
from table import Table


def resource_path(relative):
    """Получение абсолютного пути к файлу."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


class Window(QMainWindow):
    """сновной класс приложения, формирующий начальное окно"""

    def __init__(self):
        super(Window, self).__init__()
        path = resource_path('image.png')
        uic.loadUi("main.ui", self)
        user_size(self)
        center(self)
        self.userRight = None
        self.userName = None
        # Меню
        self.mlogin.setStatusTip('Войти')
        self.mlogin.triggered.connect(self.menu_login)
        self.readme.triggered.connect(lambda: os.startfile(r'Readme.txt'))
        self.autor.aboutToShow.connect(self.set_menu)  # Добавляем в меню Выход, если залогинен пользователь.
        self.autor.triggered.connect(self.exit_menu)
        self.reg.setStatusTip('Зарегистрироваться')
        # Кнопки
        self.reg.triggered.connect(self.menu_reg)
        self.bview.clicked.connect(self.view)
        self.bset.clicked.connect(self.set)

    def exit_menu(self):
        """Меню Выход"""
        self.userRight = None
        self.userName = None

    def set_menu(self):
        """ Добавляем в меню Выход и скрываем Вход/Регистрация, если залогинен пользователь."""
        if self.userName is None:
            self.mexit.setVisible(False)
            self.mlogin.setVisible(True)
            self.reg.setVisible(True)
        else:
            self.mexit.setVisible(True)
            self.mexit.setVisible(True)
            self.mexit.setStatusTip('Выйти')
            self.mlogin.setVisible(False)
            self.reg.setVisible(False)

    def menu_login(self):
        """Меню Войти"""
        self.wlogin = Login_window(self)
        self.wlogin.show()
        self.wlogin.adminSignal[str].connect(self.view)
        self.wlogin.teacherSignal[str].connect(self.view)

    def menu_reg(self):
        """Меню Регистрация"""
        wlogin = Reg_window(self)
        wlogin.exec_()

    def view(self):
        """Кнопка Просмотр расписания - отображение расписание в зависимости от пользователя"""
        self.hide()
        self.child_wnd = Table(self.userName, self)
        self.child_wnd.show()

    def set(self):
        """Кнопка Задать расписание - доступна только для администратора"""
        if self.userRight == 'admin':
            self.close()
            self.wnd = Table(self.userName, self, clear=True)
            self.wnd.show()
        else:
            login_error = QMessageBox.information(self, 'Ошибка авторизации',
                                                  "Для внесения изменений авторизуйтесь, пожалуйста.")
            if login_error == QMessageBox.Ok:
                self.menu_login()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.show()
    sys.exit(app.exec())
