from PyQt5.QtWidgets import QDesktopWidget


def center(widget):
    qr = widget.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    widget.move(qr.topLeft())


def user_size(widget):
    # изменение размеров окна в зависимости от параметров пользовательского мотитора
    my_width, my_height = 1920, 1080  # Размеры моего экрана для масштабирования
    user_height = QDesktopWidget().availableGeometry().height()
    user_width = QDesktopWidget().availableGeometry().width()
    new_height = widget.height() * user_height // my_height
    new_width = widget.width() * user_width // my_width
    widget.resize(new_width * 2, new_height * 2)
