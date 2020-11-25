import sys
#import pyqt5_tools
from PyQt5 import uic,QtCore
from PyQt5.QtWidgets import QWidget,QApplication,QDialog,QDesktopWidget,QMessageBox
import sqlite3

class Login_window(QDialog):
    adminSignal = QtCore.pyqtSignal(str)
    teacherSignal = QtCore.pyqtSignal(str)
    def __init__(self,parent=None):
        # поскольку окло логина может вызываться из родительского окна, обязательно добавить аргумент parent
        super(Login_window,self).__init__()
        uic.loadUi("login.ui",self)
        self.user_size(1920,1080)
        self.center()
        self.par=parent
        self.login_button.accepted.connect(self.on_click)
        # self.login_button.rejected.connect(sys.exit) exit закрывает родительское окно???
        self.login_button.rejected.connect(self.exec)
    def stupid_test(self,name): # проверка на дурака
        return name.isalpha()

    def on_click(self):
        if self.stupid_test(self.luser.text()):
            con = sqlite3.connect('db1.db')
            cur = con.cursor()
            result = cur.execute(
                'SELECT login, password FROM user').fetchall()

            for record in result:

                true_login=False
                if str(record[0])==self.luser.text():
                    if str(record[1])==self.lpassword.text():

                        psw = cur.execute(
                            'SELECT user.login,rights.admin FROM user,rights WHERE user.id=rights.id').fetchall()

                        dic=dict(psw)
                        if dic[str(self.luser.text())]==1:#является админом
                            self.par.userRight = 'admin'
                            self.par.userName = self.luser.text()
                            self.adminSignal.emit(self.luser.text())
                        else:
                            self.par.userRight = 'teacher'
                            self.par.userName = self.luser.text()
                            self.teacherSignal.emit(self.luser.text())

                    else:
                        QMessageBox.about(self, "Ошибка входа", "Неверный пароль")
                        self.show()# в стандартном accepted окно закрывается, открываем заново
                    true_login = True
                    break

            con.close()
            if not true_login:
                QMessageBox.about(self, "Ошибка входа", "Неверное имя пользователя")
                self.show()# в стандартном accepted окно закрывается, открываем заново

        else:
            QMessageBox.about(self, "Ошибка входа", "Логин содержит только символы")

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def user_size(self,my_width,my_height):
        # изменение размеров окна в зависимости от параметров пользовательского мотитора
        user_height = QDesktopWidget().availableGeometry().height()
        user_width = QDesktopWidget().availableGeometry().width()
        new_height= self.height()*user_height//my_height
        new_width=self.width() *user_width//my_width
        self.resize(new_width*2,new_height*2)
if __name__=='__main__':
    app=QApplication(sys.argv)
    lgn=Login_window()
    lgn.show()
    sys.exit(app.exec())




