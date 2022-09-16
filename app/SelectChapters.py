import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QDialog

from . import show_error
from .threads import ChaptersThread


class SelectChapters(QDialog):
    def __init__(self, parent, selected, session=requests.Session(), addon=''):
        super(SelectChapters, self).__init__(parent, Qt.WindowCloseButtonHint)

        uic.loadUi('ui/select.ui', self)

        self.selected = selected
        self.selected_addon = addon
        self.session = session

        self.initUi()

        self.chapters = None
        self.selected_chapters = []

        self.fetch_chapters()

    def initUi(self):
        self.select_info.setText(' '.join((self.selected, self.selected_addon)))

        self.confirm_btn.clicked.connect(self.accept)

    def fetch_chapters(self):
        worker = ChaptersThread(self, self.selected, self.session)
        worker.sending.connect(lambda: self.status_info.setText('Отправка запроса...'))
        worker.done[list].connect(self.worker_done)
        worker.error[str].connect(self.worker_fail)
        worker.start()

    def worker_done(self, result: list):
        self.status_info.setText('Готово! Выберите главы.')
        self.chapters = result
        for item in result:
            self.main_list.addItem(f'Глава {item[1]}{" - ПЛАТНАЯ!!" if item[2] else ""}')
        self.confirm_btn.setEnabled(True)

    def worker_fail(self, msg: str):
        self.status_info.setText('Ошибка получения глав')
        show_error(self, f'Ошибка получения глав:\n{msg}')

    def get_list_items(self):
        items = []
        for x in range(self.main_list.count()):
            items.append(self.main_list.item(x))
        return items

    def exec_(self) -> list:
        super(SelectChapters, self).exec_()
        items = self.get_list_items()
        for item in self.main_list.selectedItems():
            self.selected_chapters.append(self.chapters[items.index(item)])
        return self.selected_chapters
