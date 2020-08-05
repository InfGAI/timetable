import sys
import pyqt5_tools
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QApplication,QDialog,QDesktopWidget

class Reg_window(QDialog):
    def __init__(self,parent=None):
        # поскольку окло логина может вызываться из родительского окна, обязательно добавить аргумент parent
        super(Reg_window,self).__init__()
        uic.loadUi("registration.ui",self)
        self.user_size(1920,1080)
        self.center()
        self.reg_button.accepted.connect(self.on_click)
        # self.login_button.rejected.connect(sys.exit) exit закрывает родительское окно???
        self.reg_button.rejected.connect(self.exec)
    def on_click(self):
        print('hhhhhh')
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



