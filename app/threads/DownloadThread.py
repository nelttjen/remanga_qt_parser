import logging

import requests
from PyQt5.QtCore import QObject


class DownloadThread(QObject):
    def __init__(self, link, save_to, num, session=requests.Session(), key=''):
        super(DownloadThread, self).__init__()

        self.link = link
        self.save_to = save_to
        self.num = num
        self.session = session
        self.key = key

    def run(self):
        try:
            headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'}
            if self.key:
                headers['authorization'] = f'bearer {self.key}'
            print(headers)
            print(self.link)
            response = self.session.get(self.link, headers=headers)
            if response.status_code == 200:
                self.write(response.content)
            else:
                logging.error(f'{int(self.num) + 1}.jpg - status code wrong: {response.status_code}')
                raise Exception
        except:
            self.error()

    def error(self):
        try:
            with open(f'{self.save_to}/{int(self.num) + 1}_error.jpg', 'w'):
                logging.error(f'{int(self.num) + 1}.jpg - download failed')
        except Exception as e:
            logging.error(f'{int(self.num) + 1}.jpg - download failed, {e}')

    def write(self, content):
        with open(f'{self.save_to}/{int(self.num) + 1}.jpg', 'wb') as out:
            out.write(content)