import requests
from PyQt5.QtCore import QObject


class DownloadThread(QObject):
    def __init__(self, link, save_to, num, session=requests.Session()):
        super(DownloadThread, self).__init__()

        self.link = link
        self.save_to = save_to
        self.num = num
        self.session = session

    def run(self):
        try:
            response = self.session.get(self.link)
            if response.status_code == 200:
                self.write(response.content)
            else:
                raise Exception
        except:
            self.error()

    def error(self):
        with open(f'{self.save_to}/{int(self.num) + 1}_error.jpg'):
            pass

    def write(self, content):
        with open(f'{self.save_to}/{int(self.num) + 1}.jpg', 'wb') as out:
            out.write(content)