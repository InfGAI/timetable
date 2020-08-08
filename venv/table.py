import pyqt5_tools
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QApplication,QPushButton,QMainWindow,QAction,QDesktopWidget,QTableWidgetItem
from login import Login_window
from registration import Reg_window
import sqlite3

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
    def __init__(self, parent=None):
        super(Table, self).__init__()

        self.parrent = parent  # так получаем сыылку на родительское окно для использования на кнопке назад
        uic.loadUi("table.ui", self)
        self.user_size(1920, 1080)  # подставляем разрешение рабочего экрана
        self.center()  # размещение окна по центру
        # self.table.cellClicked.connect(self.on_click) #клик по ячейке
        self.bback.clicked.connect(self.back)  # Кнопка НАЗАД
        self.bsave.clicked.connect(self.save)  # Кнопка НАЗАД

        self.bcancel.clicked.connect(self.cancel)  # Кнопка НАЗАД
        # заполнение таблицы из бд
        self.fill_table()

    def save(self):
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                if self.tableWidget.item(row, column):
                    "INSERT INTO thirst (tovar, type) VALUES ('Potato', 1)"
                    print(self.tableWidget.item(row, column).text(), end=' ')
            print()

    def cancel(self):
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                if self.tableWidget.item(row, column):
                    self.tableWidget.setItem(row, column, None)
        self.fill_table()

    def fill_table(self):
        con = sqlite3.connect('db1.db')
        cur = con.cursor()
        result = cur.execute(
            'SELECT timetable.lesson,user.name FROM timetable,user WHERE timetable.id=user.id  ').fetchall()
        print(result)
        for lesson in result:
            column, row = map(int, lesson[0].split())
            print(column, row)
            self.tableWidget.setItem(row, column, QTableWidgetItem(lesson[1]))

        con.close()
    def back(self):
        self.parrent.show()  # показываем родительское окно
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


