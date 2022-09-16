from PyQt5.QtWidgets import QMessageBox


def show_error(parrent, text, caption='Ошибка'):
    QMessageBox.critical(parrent, caption, text, QMessageBox.Ok)


def show_info(parrent, text, caption='Информация'):
    QMessageBox.information(parrent, caption, text, QMessageBox.Ok)