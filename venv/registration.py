"""Модуль регистрации пользователей"""
import sqlite3

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QDialog

from functions import center, user_size
from table import Table


class Reg_window(QDialog):
    def __init__(self, parent=None):
        super(Reg_window, self).__init__()
        uic.loadUi("registration.ui", self)
        user_size(self)
        center(self)
        self.par = parent
        self.reg_button.accepted.connect(self.on_click)
        self.reg_button.rejected.connect(self.exec)
        self.group_lines = [self.luser, self.lpassword, self.lsurname, self.lname]

    def check_fill_lines(self, group):
        return all(group)


    def check_right_lines(selfself, group):
        result = True
        for item in group:
            if not item.text():
                result = False
                item.setText('Заполните поле')
            elif item.text() == 'Заполните поле':
                result = False
                color = QtCore.Qt.red
                palette = item.palette()
                palette.setColor(QtGui.QPalette.Text, color)
                item.setPalette(palette)
        return result

    def accept(self):
        if not self.check_fill_lines(self.group_lines):
            super().accept()


    def on_click(self):
        if self.check_right_lines(self.group_lines):
            con = sqlite3.connect('timetable.db')
            cur = con.cursor()
            sql = f'SELECT * FROM user WHERE login="{self.luser.text()}"'
            uid = cur.execute(sql).fetchall()
            if uid:
                QMessageBox.about(self, "Error", "Пользователь с таким именем уже существует")
            elif self.lpassword.text() != self.lrepeat.text():
                QMessageBox.about(self, "Error", "Пароли различаются")
            else:
                if self.r_admin.isChecked():
                    admin = 1
                    self.userRight = 'admin'
                else:
                    admin = 0
                    self.userRight = 'teacher'
                sql = '''INSERT INTO user(login,password,surname,name) VALUES (?, ?,?,?)'''
                cur.execute(sql, (self.luser.text(), self.lpassword.text(), self.lsurname.text(), self.lname.text()))
                sql = 'SELECT MAX(id) FROM user'
                try:
                    uid = cur.execute(sql).fetchone()[0]
                except ValueError as e:
                    uid = 1
                sql = '''INSERT INTO rights VALUES (?, ?)'''
                cur.execute(sql, (uid, admin))
                con.commit()
                self.ok = True
                QMessageBox.about(self, "ОK", "Регистрация успешна")
                self.par.userRight = self.userRight
                self.par.userName = self.luser.text()
                self.hide()
        else:
            msg = QMessageBox.about(self, "Error", "Заполните поля")
