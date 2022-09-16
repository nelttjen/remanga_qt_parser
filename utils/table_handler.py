import gspread

from utils import Settings


class TableHandler:
    def __init__(self):
        self.gc = gspread.service_account(filename='api.json')
        self.wb = self.gc.open(Settings.workspace)
        self.ws = self.wb.worksheet(Settings.sheetname)

    def get_only_ids(self, offset=1):
        return self.ws.col_values(Settings.id_column)[offset:]

    def get_info_for_view(self, offset=1):

        ret = []

        indexes = self.ws.col_values(Settings.index_column)[offset:]
        names = self.ws.col_values(Settings.name_column)[offset:]
        links = self.ws.col_values(Settings.link_column)[offset:]
        ids = self.ws.col_values(Settings.id_column)[offset:]
        for i in range(len(ids)):
            ret.append((indexes[i], names[i], ids[i], links[i]))
        return ret
