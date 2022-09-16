import json
import os

import requests

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from . import show_error, show_info, SelectChapters
from .threads import DownloadQueueThread
from utils import TableHandler, save_setts, Settings


class Window(QMainWindow):
    def __init__(self, th: TableHandler, settings=None):
        super(Window, self).__init__()

        uic.loadUi('ui/main.ui', self)
        self.setFixedSize(self.width(), self.height())
        self.initUi()
        self.update_text = lambda: self.selected_info.setText(self.selected)

        self.th = th
        self.items = []
        self.init_search()

        self.settings = settings
        self.download_folder = settings.get('save_directory', '')
        if self.download_folder:
            self.folder_status.setText('Папка выбрана')

        self.session = requests.Session()
        self.selected = None
        self.addon = ''

        self.download_queue = None
        self.is_running = False

    def init_search(self):
        self.items = self.th.get_info_for_view()
        for item in self.items:
            self.main_list.addItem(f'{item[0]}: ({item[2]}) - {item[1]}   ---   {item[3]}')

    def initUi(self):
        self.setWindowTitle(f'{Settings.TITLE} v{Settings.VERSION}')
        self.setWindowIcon(QIcon('ui/icon.ico'))

        self.select_chapters.clicked.connect(self.select_chapters_def)
        self.folder_btn.clicked.connect(self.set_folder)
        self.download_chapters.clicked.connect(self.download_thread)

        self.search_editText.textChanged[str].connect(self.search)
        self.main_list.itemClicked.connect(self.select_item)

    def set_folder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Выбор папки..."))
        if file:
            try:
                with open(f'{file}\\test.temp', 'w'):
                    pass
                try:
                    os.remove(f'{file}\\test.temp')
                except:
                    pass
                self.settings['save_directory'] = file
                save_setts(self.settings)
                self.download_folder = file
                self.folder_status.setText('Папка выбрана')
            except Exception as e:
                show_error(self, f'Нет прав на запись файлов в эту папку\n{e}')

    def search(self, text):

        self.main_list.clear()

        id_mode = False
        if text.startswith('id'):
            text = text.replace('id', '')
            id_mode = True

        for item in self.items:
            if id_mode:
                self.main_list.addItem(f'{item[0]}: ({item[2]}) - {item[1]}   ---   {item[3]}') \
                    if text == item[0] else None
            else:
                if any([text.lower() in str(_iter).lower() for _iter in [item[0], item[1], item[2], item[3]]]):
                    self.main_list.addItem(f'{item[0]}: ({item[2]}) - {item[1]}   ---   {item[3]}')

    def select_item(self, item):
        self.selected = item.text().split('(')[1].split(')')[0]
        self.addon = item.text().split(')')[1][3:].split('   ---   ')[0]
        self.update_text()

    def select_chapters_def(self):
        if self.selected is not None:
            wind = SelectChapters(self, self.selected, self.session, addon=f'({self.addon})')
            wind.show()
            result = wind.exec_()
            self.count_info.setText(str(len(result)))
            self.download_queue = result
            self.download_chapters.setEnabled(True)
        else:
            show_error(self, 'Не выбран тайтл')

    def download_thread(self):
        if self.is_running:
            show_error(self, 'Загрузка уже запущена, дождитесь её окончания')
            return
        if not self.download_folder:
            show_error(self, 'Место загрузки не выбрано')
            return
        self.is_running = True
        thread = DownloadQueueThread(self, self.download_queue, self.selected, self.download_folder, self.addon,
                                     cut_mode=self.cut_box.isChecked(), delete_after=self.cut_clear.isChecked(),
                                     session=self.session)
        thread.init.connect(lambda: self.download_info.setText('Инициализация загрузки...'))
        thread.init_cut.connect(lambda: self.download_info.setText('Инициализация нарезки...'))
        thread.init_chapter[str].connect(lambda x: self.download_info.setText(f'Инициализация загрузки, Глава {x}...'))
        thread.download_chapter[str].connect(lambda x: self.download_info.setText(f'Загрузка, Глава {x}...'))
        thread.cut_chapter[str].connect(lambda x: self.download_info.setText(f'Нарезка, Глава {x}...'))
        thread.error_chapter[str].connect(lambda x: show_error(self, f'Ошибка загрузки: Глава {x.split(";")[0]}'
                                                                     f'\n{x.split(";")[1]}'))
        thread.done.connect(self.finish)
        thread.start()

    def finish(self):
        show_info(self, 'Очередь загрузки создана, загрузка вскоре завершится')
        self.download_info.setText(f'Загрузка завершена')
        self.is_running = False