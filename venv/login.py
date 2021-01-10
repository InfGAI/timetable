"""Меню авторизации"""
import sqlite3
import sys
from functions import center, user_size
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QDesktopWidget, QMessageBox


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
        self.login_button.rejected.connect(self.exec)

    def on_click(self):
        """Кнопка ОК"""
        if self.luser.text().isalpha():  # Проверка на дурака
            con = sqlite3.connect('db1.db')
            cur = con.cursor()
            result = cur.execute('SELECT login, password FROM user').fetchall()
            for record in result:
                true_login = False
                if str(record[0]) == self.luser.text():
                    if str(record[1]) == self.lpassword.text():
                        psw = cur.execute(
                            'SELECT user.login,rights.admin FROM user,rights WHERE user.id=rights.id').fetchall()
                        dic = dict(psw)
                        if dic[str(self.luser.text())] == 1:  # является админом
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
                    true_login = True
                    break
            con.close()
            if not true_login:
                QMessageBox.about(self, "Ошибка входа", "Неверное имя пользователя")
                self.show()  # в стандартном accepted окно закрывается, открываем заново
        else:
            QMessageBox.about(self, "Ошибка входа", "Логин содержит только символы")
