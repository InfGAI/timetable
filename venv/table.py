#import pyqt5_tools
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QApplication,QMessageBox,QHeaderView,QAction,QDesktopWidget,QTableWidgetItem
from login import Login_window

import sqlite3


#модификация для вывода информации об ошибке, а не просто исключении
def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))


    QMessageBox.critical(None, 'Error', text)
    quit()


import sys

sys.excepthook = log_uncaught_exceptions



class Table(QWidget):
    def __init__(self, Uname=None,parent=None):
        super(Table, self).__init__()

        self.par = parent  # так получаем сыылку на родительское окно для использования на кнопке назад
        uic.loadUi("table.ui", self)
        self.user_size(1920, 1080)  # подставляем разрешение рабочего экрана
        self.center()  # размещение окна по центру
        # self.table.cellClicked.connect(self.on_click) #клик по ячейке
        self.bback.clicked.connect(self.back)  # Кнопка НАЗАД
        self.bsave.clicked.connect(self.save)  # Кнопка НАЗАД
        self.userName=Uname
        con = sqlite3.connect('db1.db')
        cur = con.cursor()
        self.userRight = self.par.userRight
        self.lbl_user.setText(Uname)
        self.bcancel.clicked.connect(self.cancel)  # Кнопка ОТМЕНА
        # заполнение таблицы из бд
        self.fill_table()
        # растягиваем таблицу на все пространство
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def save(self):
        ''' Сохраняет таблицу, если при сохранении выявляются дубли учеников/препоадвателей, появлется диалоговое окно'''
        if self.userRight == 'teacher':
            con = sqlite3.connect('db1.db')
            cur = con.cursor()
            teacher = self.userName
            uid = "SELECT id from user WHERE login='{}'".format(str(teacher))
            tid = cur.execute(uid).fetchall()[0][0]
            id = 'WHERE id =' + str(tid)
            sql = '''SELECT timetable.lesson,user.login,student.surname FROM timetable,user,student WHERE 
                                                    timetable.teacher_id=user.id AND student.id=timetable.student_id'''
            all_lessons=cur.execute(sql).fetchall()

            # Создаем из результата запроса к ДБ словарь, где ключ урок, а содержимое - список кортежей учитель-ученик
            dic_lesson={}

            for item in all_lessons:
                lesson,teacher,student=item

                if lesson in dic_lesson:
                    dic_lesson[lesson].append((teacher,student))
                else:
                    dic_lesson[lesson]=[(teacher, student)]
            # Сравниваем текущее состояние таблицы со словарем
            print(dic_lesson)
            for row in range(self.tableWidget.rowCount()):
                for column in range(self.tableWidget.columnCount()):
                    lesson=str(row)+' '+str(column)
                    if self.tableWidget.item(row, column): # Перебираем ячейке таблицы, где есть запись
                        if lesson not in dic_lesson: # Если вобщем расписании урок свободен, можем записать
                            record=True
                        else: # Если в общем расписании на этом уроке есть занятия

                            sql = "SELECT timetable.lesson, user.login FROM timetable,student,user WHERE user.id=timetable.teacher_id AND student.id=timetable.student_id AND student.surname='"+self.tableWidget.item(row, column).text()+"'"
                            student_lessons = dict(cur.execute(sql).fetchall())
                            if lesson in student_lessons:  # Проверяем уроки уже существующие в общем расписании
                                if student_lessons[lesson]!=self.userName: # у ученика не может быть несколько уроков одновременно
                                    save_error = QMessageBox.information(self, 'Ошибка сохранения',
                                                                          "У {} уже занят урок {}".format(self.tableWidget.item(row, column).text(),lesson))
                                record = False


                            else: # Проверяем, что не произошло изменений в существующих записях
                                record = True
                                for lesson_in_tt in filter(lambda x: x[0]==self.userName,dic_lesson[lesson]):
                                    if lesson_in_tt[1]!=self.tableWidget.item(row, column).text():
                                        add_student_error = QMessageBox.information(self, 'Ошибка сохранения',
                                                                            "Перенос занятий {} должен быть согласован администратором".format(
                                                                                lesson_in_tt[1]))
                                        self.fill_table()
                                        record = False
                                        break


                        if record:
                            student = self.tableWidget.item(row, column).text()
                            sql = "SELECT id from student WHERE surname='{}'".format(str(student))
                            sid=cur.execute(sql).fetchall()
                            if sid:
                                sid = sid[0][0]
                            else:
                                sql = 'SELECT MAX(id) FROM student'
                                sid = cur.execute(sql).fetchall()[0][0]+1
                                sql = '''INSERT INTO student(id,surname) VALUES (?, ?)'''  # по id записываем уроки в расписание
                                cur.execute(sql, (sid, student))



                            sql = '''INSERT INTO timetable(teacher_id, lesson,student_id) VALUES (?, ?,?)'''  # по id записываем уроки в расписание
                            cur.execute(sql, (tid, lesson,sid))





            con.commit()

        else:
            login_error = QMessageBox.information(self, 'Ошибка авторизации',
                                                  "Для внесения изменений авторизуйтесь, пожалуйста.")
            if login_error==QMessageBox.Ok:
                self.menu_login()


 #   def change(self):



    def cancel(self):
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                if self.tableWidget.item(row, column):
                    self.tableWidget.setItem(row, column, None)
        self.fill_table()

    def fill_table(self):
        con = sqlite3.connect('db1.db')
        cur = con.cursor()
        sql = '''SELECT timetable.lesson FROM timetable'''
        result = cur.execute(sql).fetchall()
        if self.userRight == 'admin' or self.userRight == None:
            sql = '''SELECT DISTINCT timetable.lesson FROM timetable''' # Выбираем все существующие уроки в расписании
        else:
            sql = '''SELECT DISTINCT timetable.lesson FROM timetable,user WHERE 
                    timetable.teacher_id=user.id AND user.login="{}"'''.format(self.userName) # Выбираем все существующие уроки данного учителя в расписании

        result=cur.execute(sql).fetchall()
        for item in result:
            row,column=map(int,item[0].split())
            if self.userRight == 'admin' or self.userRight == None:
                sql= '''SELECT user.name, student.surname FROM timetable,user,student WHERE
                        timetable.teacher_id=user.id AND student.id=timetable.student_id AND timetable.lesson="{}"'''.format(item[0])
                self.bcancel.hide()
                self.bsave.hide()
                self.resize(self.width()*1.03,self.height()*1.02)
                self.center()
                day = '\n'.join([' '.join(list(item)) for item in cur.execute(sql).fetchall()])
            else:
                sql = '''SELECT student.surname FROM timetable,user,student WHERE
                                        timetable.teacher_id=user.id AND student.id=timetable.student_id AND timetable.lesson="{}" AND user.login="{}"'''.format(item[0],self.userName)
                day = cur.execute(sql).fetchone()[0]


            self.tableWidget.setItem(row,column, QTableWidgetItem(day))
        con.close()

    def back(self):
        self.par.show()  # показываем родительское окно
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
        self.wlogin = Login_window(self)
        self.wlogin.show()



if __name__=='__main__':
    app=QApplication(sys.argv)
    wnd=Table()
    wnd.show()
    sys.exit(app.exec())


