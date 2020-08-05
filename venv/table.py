import pyqt5_tools
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QApplication,QPushButton,QMainWindow,QAction,QDesktopWidget
from login import Login_window
from registration import Reg_window

#модификация для вывода информации об ошибке, а не просто исключении
def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print(text)
    QtWidget.QMessageBox.critical(None, 'Error', text)
    quit()


import sys

sys.excepthook = log_uncaught_exceptions



class Table(QWidget):
    def __init__(self,parent=None):
        super(Table,self).__init__()
        uic.loadUi("table.ui",self)
        self.user_size(1920,1080) #подставляем разрешение рабочего экрана
        self.center() # размещение окна по центру

        self.bback.clicked.connect(self.back)
    def back(self):
        self.close()

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
        self.resize(new_width*2,new_height*2) # размеры половинчатые???

    def menu_login(self):
        wlogin = Login_window(self)
        wlogin.exec_()
    def menu_reg(self):
        wlogin = Reg_window(self)
        wlogin.exec_()

if __name__=='__main__':
    app=QApplication(sys.argv)
    wnd=Table()
    wnd.show()
    sys.exit(app.exec())


