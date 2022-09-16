from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    workspace: str = 'Группа ВК'
    sheetname: str = 'Техническое'

    index_column = 1
    name_column = 2
    link_column = 3

    id_column = 5

    endpoint = 'https://api.remanga.org/api/titles/chapters/'

    VERSION = 1.0
    TITLE = 'ReManga parser'
