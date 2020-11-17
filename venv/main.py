# import pyqt5_tools
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QApplication,QMessageBox,QMainWindow,QAction,QDesktopWidget
from login import Login_window
import os
from registration import Reg_window
from table import Table

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


#модификация для вывода информации об   ошибке, а не просто исключении
def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback

    text += ''.join(traceback.format_tb(tb))

    print(text)
    QMessageBox.critical(None, 'Error', text)
    quit()


import sys

sys.excepthook = log_uncaught_exceptions



class Window(QMainWindow):
    def __init__(self):
        super(Window,self).__init__()
        path = resource_path('image.png')
        uic.loadUi("main.ui",self)
        self.user_size(1920,1080) #подставляем разрешение рабочего экрана
        self.center() # размещение окна по центру
        #loginAction = QAction("login",self)
        #self.login.setShortcut('Ctrl+Q')
        #при создании из дизайнера, виджеты уже являются QAction
        self.userRight = None
        self.userName = None
        # кнопка Войти
        self.mlogin.setStatusTip('Войти')
        self.autor.aboutToShow.connect(self.set_menu)
        self.autor.triggered.connect(self.exit_menu)
        self.mlogin.triggered.connect(self.menu_login)
        # кнопка Регистарция
        self.reg.setStatusTip('Зарегистрироваться')
        if self.userRight != None:
            self.bset.setEnabled(True)
        else:
            self.bset.setEnabled(False)
        self.reg.triggered.connect(self.menu_reg)
        self.bview.clicked.connect(self.view)
        self.bset.clicked.connect(self.set)

    def exit_menu(self):
        self.userRight=None
        self.userName=None

    def set_menu(self):
        ''' Добавляем в меню Выход, если залогинен пользователь'''
        if self.userName==None:
            self.mexit.setVisible(False)
        else:
            self.mexit.setVisible(True)
            self.mexit.setStatusTip('Выйти')

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
        new_height= self.height()*user_height//my_height
        new_width=self.width() *user_width//my_width
        self.resize(new_width*2,
                    new_height*2) # размеры половинчатые???

    def menu_login(self):
        self.wlogin = Login_window(self)
        self.wlogin.show()
        self.wlogin.adminSignal[str].connect(self.view)
        self.wlogin.teacherSignal[str].connect(self.view)
    def menu_reg(self):
        wlogin = Reg_window(self)
        wlogin.exec_()

    def view(self,n):
        self.hide()

        self.child_wnd = Table(self.userName,self)
        self.child_wnd.show()

    def set(self,n):
        if self.userRight != None:
            self.userName = n
            self.close()
            self.wnd = Table(self,n)
            self.wnd.show()
        else:
            login_error = QMessageBox.information(self, 'Ошибка авторизации',
                                                  "Для внесения изменений авторизуйтесь, пожалуйста.")
            if login_error == QMessageBox.Ok:
                self.menu_login()


if __name__=='__main__':
    app=QApplication(sys.argv)
    wnd=Window()
    wnd.show()
    sys.exit(app.exec())


