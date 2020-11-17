import sys
#import pyqt5_tools
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox,QApplication,QDialog,QDesktopWidget
import sqlite3
from table import Table

class Reg_window(QDialog):
    def __init__(self,parent=None):
        # поскольку окло логина может вызываться из родительского окна, обязательно добавить аргумент parent
        super(Reg_window,self).__init__()
        uic.loadUi("registration.ui",self)
        self.user_size(1920,1080)
        self.center()
        self.par=parent
        self.reg_button.accepted.connect(self.on_click)
        # self.login_button.rejected.connect(sys.exit) exit закрывает родительское окно???
        self.reg_button.rejected.connect(self.exec)

    def stupid_test(self, name):
        return name.isalpha()


    def on_click(self):
        if self.stupid_test(self.luser.text()):
            con = sqlite3.connect('db1.db')
            cur = con.cursor()
            if self.r_admin.isChecked():
                admin=1
            else:
                admin=0
            sql = '''INSERT INTO user(login,password) VALUES (?, ?)'''
            cur.execute(sql, (self.luser.text(),(self.lpassword.text())))

            sql = 'SELECT MAX(id) FROM user'
            uid=cur.execute(sql).fetchall()[0][0]
            print(uid)

            sql = '''INSERT INTO rights VALUES (?, ?)'''
            cur.execute(sql, (admin,uid))
            con.commit()  # если внесены изменения не просто close

            self.close()
            self.par.userName=self.luser.text()
            self.child_wnd = Table(self.luser.text(), self)
            self.child_wnd.show()
        else:
            QMessageBox.about(self, "Ошибка регистрации", "Логин может содержать только символы")

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
    lgn=Reg_window()
    lgn.show()
    sys.exit(app.exec())




