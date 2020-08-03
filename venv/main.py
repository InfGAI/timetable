def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print(text)
    QtWidget.QMessageBox.critical(None, 'Error', text)
    quit()


import sys

sys.excepthook = log_uncaught_exceptions
#модификация для вывода информации об ошибке, а не просто исключении

import pyqt5_tools
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QApplication,QPushButton,QMainWindow,QAction,QDesktopWidget
from login import Login_window

class Window(QMainWindow):
    def __init__(self):
        super(Window,self).__init__()
        uic.loadUi("main.ui",self)
        self.user_size(1920,1080) #подставляем разрешение рабочего экрана
        self.center()
        #loginAction = QAction("login",self)
        #self.login.setShortcut('Ctrl+Q')
        #при создании из дизайнера, виджеты уже являются QAction
        self.mlogin.setStatusTip('Войти')
        self.mlogin.triggered.connect(self.menu_login)

    def center(self):
        # центрирование окна в зависимости от параметров пользовательского мотитора
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def user_size(self,my_width,my_height):
        # изменение размеров окна в зависимости от параметров пользовательского мотитора
        user_height = QDesktopWidget().availableGeometry().height()
        user_width = QDesktopWidget().availableGeometry().width()
        print(user_height,user_width)
        new_height= self.height()*user_height//my_height
        new_width=self.width() *user_width//my_width
        self.resize(new_width*2,new_height*2)

    def menu_login(self):

        wlogin = Login_window(self)
        wlogin.exec_()

if __name__=='__main__':
    app=QApplication(sys.argv)
    wnd=Window()
    wnd.show()
    sys.exit(app.exec())


