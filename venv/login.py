import sys
import pyqt5_tools
from PyQt5 import uic,QtCore
from PyQt5.QtWidgets import QWidget,QApplication,QDialog,QDesktopWidget,QMessageBox
import sqlite3

class Login_window(QDialog):
    adminSignal = QtCore.pyqtSignal()
    teacherSignal = QtCore.pyqtSignal()
    def __init__(self,parent=None):
        # поскольку окло логина может вызываться из родительского окна, обязательно добавить аргумент parent
        super(Login_window,self).__init__()
        uic.loadUi("login.ui",self)
        self.user_size(1920,1080)
        self.center()

        self.login_button.accepted.connect(self.on_click)
        # self.login_button.rejected.connect(sys.exit) exit закрывает родительское окно???
        self.login_button.rejected.connect(self.exec)
    def on_click(self):
        con = sqlite3.connect('db1.db')
        cur = con.cursor()
        result = cur.execute(
            'SELECT login, password FROM user').fetchall()
        print(result)
        for record in result:
            print(record)
            print((self.luser.text(),self.lpassword.text()))
            true_login=False
            if record[0]==self.luser.text():
                if record[1]==self.lpassword.text():
                    print('ok')
                    psw = cur.execute(
                        'SELECT user.login,rights.admin FROM user,rights WHERE user.id=rights.id').fetchall()
                    print(psw)
                    dic=dict(psw)
                    if dic[self.luser.text()]==1:#является админом
                        self.adminSignal.emit()
                    else:
                        self.teacherSignal.emit()
                else:
                    QMessageBox.about(self, "Ошибка входа", "Неверный пароль")
                true_login = True
                break

        if not true_login:
            QMessageBox.about(self, "Ошибка входа", "Неверное имя пользователя")

        con.close()
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




