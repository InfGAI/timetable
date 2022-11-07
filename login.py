"""Меню авторизации"""
import sqlite3

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox

from functions import center, user_size


class Login_window(QDialog):
    """Класс окна авторизации"""
    adminSignal = QtCore.pyqtSignal(str)
    teacherSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        """QDialog авторизации
        :param parent: родительскмй виджет
        """
        super(Login_window, self).__init__()
        uic.loadUi("login.ui", self)
        user_size(self)
        center(self)
        self.par = parent
        self.login_button.accepted.connect(self.on_click)

    def on_click(self):
        """Кнопка ОК"""
        if self.luser.text().isdigit():
            sur = int(self.luser.text())
        else:
            sur = self.luser.text()
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        result = cur.execute(f'SELECT password FROM user WHERE login="{sur}"').fetchone()
        if result:
            if str(result[0]) == self.lpassword.text():
                psw = cur.execute(
                    'SELECT user.login,rights.admin FROM user,rights WHERE user.id=rights.id').fetchall()
                dic = dict(psw)
                if dic[sur] == 1:  # является админом
                    self.par.userRight = 'admin'
                    self.par.userName = self.luser.text()
                    self.adminSignal.emit(self.luser.text())
                else:
                    self.par.userRight = 'teacher'
                    self.par.userName = self.luser.text()
                    self.teacherSignal.emit(self.luser.text())
            else:
                QMessageBox.about(self, "Ошибка входа", "Неверный пароль")
                self.show()  # в стандартном accepted окно закрывается, открываем заново
        else:
            QMessageBox.about(self, "Ошибка входа", "Неверное имя пользователя")
            self.show()  # в стандартном accepted окно закрывается, открываем заново
        con.close()
