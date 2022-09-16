import requests

from PyQt5.QtCore import pyqtSignal, QThread

from utils import Settings


class ChaptersThread(QThread):

    sending = pyqtSignal()
    error = pyqtSignal(str)
    done = pyqtSignal(list)

    def __init__(self, parent, select, session: requests.Session):
        super(ChaptersThread, self).__init__(parent)
        self.select = select
        self.session = session

    def run(self):
        self.sending.emit()
        sign_val = []
        endpoint = Settings.endpoint
        data = {
            'branch_id': self.select,
            'count': 9999,
            'ordering': 'index',
            'page': 1,
        }
        try:
            resp = self.session.get(endpoint, params=data).json()
            for item in resp.get('content'):
                new_tuple = (item.get('id'), item.get('index'), item.get('is_paid'))
                sign_val.append(new_tuple)
            self.done.emit(sign_val)
        except Exception as e:
            self.error.emit(e.__str__())

