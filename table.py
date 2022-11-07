"""Модуль отображения таблицы расписания"""
import csv
import sqlite3
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QHeaderView, QTableWidgetItem, \
    QFileDialog
from functions import center, user_size
from login import Login_window


class Table(QWidget):
    """Основной класс таблицы расписания"""
    weeks_day = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    def __init__(self, Uname=None, parent=None, clear=False):
        """Созадет QWidget таблицу расписания
        :param Uname: пользователь
        :param Uname: пользователь
        :param parent: родительское окно
        :param clear: True - пустая таблица
        """
        super(Table, self).__init__()
        self.clear = clear
        self.par = parent  # так получаем сыылку на родительское окно для использования на кнопке назад
        uic.loadUi("table.ui", self)
        user_size(self)
        center(self)
        self.userName = Uname
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        self.userRight = self.par.userRight
        self.lbl_user.setText(Uname)
        # Описание кнопок
        self.bsave.setEnabled(False)
        self.bcancel.setEnabled(False)
        self.bback.clicked.connect(self.back)  # Кнопка НАЗАД
        self.bsave.clicked.connect(self.save)  # Кнопка СОХРАНИТЬ
        self.bimport.clicked.connect(self.import_table)  # Кнопка ЗАГРУЗИТЬ РАСПИСАНИЕ
        self.bexport.clicked.connect(self.export_table)  # Кнопка СОХРАНИТЬ РАСПИСАНИЕ
        self.bcancel.clicked.connect(self.cancel)  # Кнопка ОТМЕНА
        # заполнение таблицы из бд
        if not clear:
            self.fill_table()
        # растягиваем таблицу на все пространство
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalSlider.valueChanged[int].connect(self.changeValue)
        if self.userRight is None:
            self.bcancel.hide()
            self.bsave.hide()
            self.bimport.hide()
        elif self.userRight == 'teacher':
            self.bimport.hide()
        if not clear:
            self.bimport.hide()
        self.table.cellChanged.connect(self.check_change)

    def check_change(self):
        self.bsave.setEnabled(True)
        self.bcancel.setEnabled(True)

    def changeValue(self, value):
        """Изменение размера шрифта таблицы
        :param value: размер шрифта
        """
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                if self.table.item(row, column):
                    self.table.item(row, column).setFont(QtGui.QFont("Times", 5 + value))

    def save(self):
        """Кнопка СОХРАНИТЬ"""
        self.bcancel.setEnabled(False)
        self.bsave.setEnabled(False)
        if self.clear:
            clear_error = QMessageBox.question(self, "ВНИМАНИЕ!!!", "Действие уничтожит существующее расписание!!!",
                                               QMessageBox.Yes | QMessageBox.No)
            if clear_error == QMessageBox.Yes:
                self.save_changes()
            else:
                self.fill_table()
        else:
            self.save_changes()

    def save_changes(self):
        """Сохраняет таблицу, если при сохранении выявляются дубли учеников/препоадвателей, появлется диалоговое окно"""
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        sql = '''SELECT timetable.lesson,user.login,student.surname FROM timetable,user,student WHERE 
                                                timetable.teacher_id=user.id AND student.id=timetable.student_id'''
        all_lessons = cur.execute(sql).fetchall()
        # Создаем из результата запроса к ДБ словарь, где ключ урок, а содержимое - список кортежей учитель-ученик
        dic_lesson = {}
        for item in all_lessons:
            lesson, teacher, student = item
            if lesson in dic_lesson:
                dic_lesson[lesson].append((teacher, student))
            else:
                dic_lesson[lesson] = [(teacher, student)]

        if self.userRight == 'teacher':
            teacher = self.userName
            record_ok = True  # Внесены ли изменения в таблицу
            record = True  # пишем ли текущую ячейку
            uid = "SELECT id from user WHERE login='{}'".format(str(teacher))
            tid = cur.execute(uid).fetchone()[0]

            # Сравниваем текущее состояние таблицы со словарем
            for row in range(self.table.rowCount()):
                for column in range(self.table.columnCount()):
                    record = True
                    lesson = str(row) + ' ' + str(column)
                    # Для всех непустх ячеек

                    if self.table.item(row, column) and self.table.item(row,
                                                                        column).text().strip():  # Перебираем ячейке таблицы, где есть запись
                        student = self.table.item(row, column).text().strip()
                        if lesson in dic_lesson:
                            # Если в общем расписании на этом уроке есть занятия
                            sql = "SELECT timetable.lesson, user.login FROM timetable,student,user WHERE user.id=timetable.teacher_id AND student.id=timetable.student_id AND student.surname='" + student + "'"
                            student_lessons = dict(cur.execute(sql).fetchall())
                            # Проверяем уроки студента уже существующие в общем расписании
                            if lesson in student_lessons:
                                record = False  # не пишем этот урок в БД
                                if student_lessons[lesson] != self.userName:
                                    # у ученика не может быть несколько уроков одновременно у разных учителей
                                    record_ok = False  # не обновляем БД
                                    save_error = QMessageBox.information(self, 'Ошибка сохранения',
                                                                         "У {} уже занят {} {}й урок.".format(
                                                                             student,
                                                                             self.weeks_day[column], str(row + 1)))
                                    self.table.setItem(row, column, QTableWidgetItem(''))
                                    break  # ошибка - дальше проверять нет смысла

                            # Если это замена ученика на уроке
                            sql = f'SELECT student.surname FROM timetable,student,user WHERE ' \
                                  f'user.id=timetable.teacher_id AND student.id=timetable.student_id AND' \
                                  f' timetable.lesson="{lesson}" AND user.login="{teacher}"'
                            print(sql)
                            student_in_bd = [i[0] for i in cur.execute(sql).fetchall()]
                            print(sql)
                            if student_in_bd and student not in student_in_bd:
                                record_ok = False
                                record = False
                                QMessageBox.information(self, 'Ошибка сохранения',
                                                        "Изменение расписания должно быть согласовано с координатором")
                                break

                        if record:
                            record_ok = True
                            sql = f"SELECT id from student WHERE surname='{student}'"
                            student_exist = cur.execute(sql).fetchone()
                            if not student_exist:
                                sql = f'''INSERT INTO student(surname) VALUES ("{student}")'''  # по id записываем уроки в расписание
                                cur.execute(sql)
                                sql = 'SELECT MAX(id) FROM student'
                                sid = cur.execute(sql).fetchone()[0]
                            else:
                                sid=student_exist[0]
                            sql = '''INSERT INTO timetable(teacher_id, lesson,student_id) VALUES (?, ?,?)'''  # по id записываем уроки в расписание
                            cur.execute(sql, (tid, lesson, sid))
                    else:
                        if lesson in dic_lesson:
                            cur.execute(f'DELETE FROM timetable WHERE lesson="{lesson}" and teacher_id="{tid}"')
                            record_ok = True
                if not record_ok:
                    break
            if record_ok:
                con.commit()
                clear_error = QMessageBox.information(self, "ОК", "Расписание обновлено.")
        elif self.userRight == 'admin':
            sql = "SELECT surname,id from user"
            dic_tid = dict(cur.execute(sql).fetchall())
            sql = "SELECT surname,id from student"
            dic_sid = dict(cur.execute(sql).fetchall())
            sid = 1
            cur.execute('DELETE FROM timetable')
            value_error = None
            all_student = set()
            all_teachers = set()
            for row in range(self.table.rowCount()):
                for column in range(self.table.columnCount()):
                    lesson = str(row) + ' ' + str(column)
                    if self.table.item(row, column) and self.table.item(row,
                                                                        column).text().strip():  # Перебираем ячейке таблицы, где есть запись
                        for item in self.table.item(row, column).text().strip().split('\n'):
                            try:
                                teacher, student = item.split()
                            except ValueError as e:
                                value_error = QMessageBox.information(self, "ОК", "Неверный формат записей. "
                                                                                  "Уроки должны вноситься в формате "
                                                                                  "Фамилия_преподавателя "
                                                                                  "Фамилия_ученика через пробел.")
                                break
                            sql = f'''SELECT id FROM student WHERE surname = "{student}"'''
                            result = cur.execute(sql).fetchone()
                            if not result:
                                sql = f'''INSERT INTO student(surname) VALUES ("{student}")'''
                                cur.execute(sql)
                                con.commit()
                                sql = f'''SELECT MAX(id) FROM student'''
                                result = cur.execute(sql).fetchone()
                            sid = result[0]
                            sql = f'''SELECT id FROM user WHERE surname = "{teacher}"'''
                            result = cur.execute(sql).fetchone()
                            if not result:
                                sql = '''INSERT INTO user(login,password,surname) VALUES (?,?,?)'''
                                cur.execute(sql, (teacher, 123, teacher))
                                con.commit()
                                sql = f'''SELECT MAX(id) FROM user'''
                                tid = cur.execute(sql).fetchone()[0]
                                sql = '''INSERT INTO rights(id,admin) VALUES (?,?)'''
                                cur.execute(sql, (tid, "0"))
                                con.commit()
                            else:
                                tid = result[0]
                            sql = '''INSERT INTO timetable(teacher_id, lesson,student_id) VALUES (?, ?,?)'''  # по id записываем уроки в расписание
                            cur.execute(sql, (tid, lesson, sid))
                    con.commit()
            if value_error is None:
                clear_error = QMessageBox.information(self, "ОК", "Расписание обновлено.")
        else:
            login_error = QMessageBox.information(self, 'Ошибка авторизации',
                                                  "Для внесения изменений авторизуйтесь, пожалуйста.")
            if login_error == QMessageBox.Ok:
                self.menu_login()

    def import_table(self):
        """Сохранение текущего вида расписания в файл timetable.csv"""
        fname = QFileDialog.getOpenFileName(self, 'Open file')
        if fname[0][-3:]:
            if fname[0][-3:] != 'csv':
                clear_error = QMessageBox.information(self, "Ошибка", "Расписание должно быть в формате .csv")
            else:
                with open(fname[0], encoding="utf8") as csvfile:
                    reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                    self.clear_table()
                    for i, row in enumerate(reader):
                        for j, cell in enumerate(row):
                            if cell:
                                self.table.setItem(i, j, QTableWidgetItem(cell))
                save_att = QMessageBox.information(self, "Внимание.",
                                                   "Проверьте загруженное расписание, одполните его при "
                                                   "необходимости и нажмите кнопку Сохранить либо "
                                                   "Отменить для возврата к предыдущей версии.")

    def export_table(self):
        """Загрузка расписания из файла csv, для сохранения расписания в бд требуется нажать кнопку СОХРАНИТЬ"""
        with open('timetable.csv', 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i in range(self.table.rowCount()):
                row = []
                for j in range(self.table.columnCount()):
                    cell = self.table.item(i, j)
                    if cell:
                        row.append(self.table.item(i, j).text().strip())
                    else:
                        row.append('')
                writer.writerow(row)

    def cancel(self):
        """Кнопка ОТМЕНА"""
        self.clear_table()
        self.fill_table()

    def clear_table(self):
        """Кнопка ОТМЕНА"""
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                if self.table.item(row, column):
                    self.table.setItem(row, column, None)

    def fill_table(self):
        """Заполнение таблицы из бд"""
        con = sqlite3.connect('timetable.db')
        cur = con.cursor()
        if self.userRight == 'admin' or self.userRight is None:
            sql = '''SELECT DISTINCT timetable.lesson FROM timetable'''  # Выбираем все существующие уроки в расписании
        else:
            sql = '''SELECT DISTINCT timetable.lesson FROM timetable,user WHERE 
                    timetable.teacher_id=user.id AND user.login="{}"'''.format(
                self.userName)  # Выбираем все существующие уроки данного учителя в расписании
        result = cur.execute(sql).fetchall()
        for item in result:
            row, column = map(int, item[0].split())
            if self.userRight == 'admin' or self.userRight is None:
                sql = '''SELECT user.surname, student.surname FROM timetable,user,student WHERE timetable.teacher_id=user.id AND student.id=timetable.student_id AND timetable.lesson="{}"'''.format(
                    item[0])
                day = '\n'.join([' '.join(list(map(str, item))) for item in cur.execute(sql).fetchall()])
            else:
                sql = '''SELECT student.surname FROM timetable,user,student WHERE
                                        timetable.teacher_id=user.id AND student.id=timetable.student_id AND timetable.lesson="{}" AND user.login="{}"'''.format(
                    str(item[0]), self.userName)
                day = cur.execute(sql).fetchone()[0]
            self.table.setItem(row, column, QTableWidgetItem(str(day)))
        con.close()

    def back(self):
        """Кнопка НАЗАД"""
        self.par.show()  # показываем родительское окно
        self.close()

    def menu_login(self):
        """Окно авторизации"""
        self.wlogin = Login_window(self)
        self.wlogin.show()
