import sys

from PyQt5.QtWidgets import QApplication

from app.Window import Window
from utils import init_logger, TableHandler, init_settings


if __name__ == '__main__':
    init_logger()

    settings = init_settings()

    app = QApplication(sys.argv)
    wind = Window(TableHandler(), settings=settings)
    wind.show()
    app.exec_()
    sys.exit()