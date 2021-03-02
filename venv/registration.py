"""Модуль регистрации пользователей"""
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QDialog

from functions import center, user_size
from table import Table

def checkSymbol(*args):
    return any(filter(lambda x: x == 0, args))

class Reg_window(QDialog):
    def __init__(self, parent=None):
        # поскольку окло логина может вызываться из родительского окна, обязательно добавить аргумент parent
        super(Reg_window, self).__init__()
        uic.loadUi("registration.ui", self)
        user_size(self)
        center(self)
        self.par = parent
        self.reg_button.accepted.connect(self.on_click)
        self.reg_button.rejected.connect(self.exec)

    def stupid_test(self, name):
        return name.isalpha()

    def on_click(self):
        if checkSymbol(self.luser.text(), self.lpassword.text()):
            con = sqlite3.connect('db1.db')
            cur = con.cursor()
            if self.r_admin.isChecked():
                admin = 1
                self.userRight = 'admin'
            else:
                admin = 0
                self.userRight = 'teacher'
            sql = '''INSERT INTO user(login,password) VALUES (?, ?)'''
            cur.execute(sql, (self.luser.text(), (self.lpassword.text())))
            sql = 'SELECT MAX(id) FROM user'
            uid = cur.execute(sql).fetchall()[0][0]
            sql = '''INSERT INTO rights VALUES (?, ?)'''
            cur.execute(sql, (admin, uid))
            con.commit()
            self.par.userName = self.luser.text()
            self.child_wnd = Table(self.luser.text(), self)
            self.child_wnd.show()
            self.hide()
        else:
            QMessageBox.about(self, "Ошибка регистрации", "Логин может содержать только символы")
