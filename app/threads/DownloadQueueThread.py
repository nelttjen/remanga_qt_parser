import os
import shutil
import requests

from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

from utils import Settings
from .DownloadThread import DownloadThread


class DownloadQueueThread(QThread):

    init = pyqtSignal()
    init_cut = pyqtSignal()
    init_chapter = pyqtSignal(str)
    download_chapter = pyqtSignal(str)
    cut_chapter = pyqtSignal(str)
    error_chapter = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, parent, queue, selected, folder, item_name, cut_mode=False, delete_after=False, session=requests.Session()):
        super(DownloadQueueThread, self).__init__(parent)
        self.queue = queue
        self.actual_queue = {}
        self.session: requests.Session = session

        self.selected = selected
        self.folder = folder

        self.title_name = item_name
        self.cut_mode = cut_mode
        self.delete_after = delete_after
        self.folders = []

        self.threads = []

    def run(self) -> None:
        self.init.emit()
        cur_folder = self.folder + f'/{self.title_name.replace(" ", "_").lower()}_{self.selected}'
        os.mkdir(cur_folder) if not os.path.exists(cur_folder) else None
        for item in self.queue:
            self.init_chapter.emit(str(item[1]))
            item_folder = f'{cur_folder}/{item[1]}_{self.title_name.replace(" ", "_").lower()}'
            shutil.rmtree(item_folder) if os.path.exists(item_folder) else None
            os.mkdir(item_folder)
            self.folders.append(item_folder)

            links = []
            try:
                response = self.session.get(Settings.endpoint + f'/{item[0]}').json()
                for i in response.get('content').get('pages'):
                    if isinstance(i, list):
                        for j in i:
                            links.append(j.get('link'))
                    else:
                        links.append(i.get('link'))
                self.download_chapter.emit(str(item[1]))
                for i, link in enumerate(links):
                    thread = QThread()
                    worker = DownloadThread(link, item_folder, i, session=self.session)

                    worker.moveToThread(thread)

                    thread.started.connect(worker.run)
                    thread.start()
                    self.threads.append((thread, worker))
                    QThread.msleep(140)

            except Exception as e:
                self.error_chapter.emit(f'{item[1]};{e.__str__()}')
                shutil.rmtree(item_folder) if os.path.exists(item_folder) else None

        if self.cut_mode:
            self.init_cut.emit()
            QThread.msleep(5000)
            for item in self.folders:
                self.cut_chapter.emit(item.split('/')[-1])
                images_to_cut = []
                cur_items = [item + f'/{x}' for x in sorted(os.listdir(item), key=lambda x: int(x.replace('.jpg', '')))]
                os.mkdir(item + '/cut')
                os.mkdir(item + '/cut/temp')
                try:
                    width = Image.open(cur_items[0]).width
                    max_height = 65535
                    image_current = Image.new('RGB', (width, max_height))
                except Exception:
                    print(item.split('/')[-1] + ' failed')
                    continue
                count = 0
                count_img = 1
                for image in cur_items:
                    image_open = Image.open(image).convert('RGB')
                    if count + image_open.height < max_height:
                        image_current.paste(image_open, (0, count))
                        count += image_open.height
                    else:
                        image_current = image_current.crop((0, 0, width, count))
                        image_current.save(item + f'/cut/temp/{count_img}.jpg')
                        images_to_cut.append([item + f'/cut/temp/{count_img}.jpg', item])
                        count = 0
                        count_img += 1
                        image_current = Image.new('RGB', (width, max_height))
                        image_current.paste(image_open, (0, count))
                        count += image_open.height
                    if cur_items.index(image) == len(cur_items) - 1:
                        image_current = image_current.crop((0, 0, width, count))
                        image_current.save(item + f'/cut/temp/{count_img}.jpg')
                        images_to_cut.append([item + f'/cut/temp/{count_img}.jpg', item])
                count = 0
                for cut_img in images_to_cut:
                    image_pil = Image.open(cut_img[0])
                    times = image_pil.height // 2000
                    for x in range(times):
                        crop_image = image_pil.crop((0, 2000 * x, image_pil.width, 2000 * (x + 1)))
                        count += 1
                        crop_image.save(cut_img[1] + f'/cut/{count}.jpg')
                    crop_image = image_pil.crop((0, 2000 * times, image_pil.width, image_pil.height))
                    count += 1
                    crop_image.save(cut_img[1] + f'/cut/{count}.jpg')
                shutil.rmtree(item + '/cut/temp') if os.path.exists(item + '/cut/temp') else None
                if self.delete_after:
                    items = os.listdir(item)
                    for image in items:
                        if image != 'cut':
                            try:
                                os.remove(item + f'/{image}')
                            except Exception as e:
                                continue
        self.done.emit()