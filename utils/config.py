import json
import os

CONFIG_DEFAULT = {
    'save_directory': '',
}


def init():
    os.mkdir('.\\temp') if not os.path.exists('.\\temp') else None
    if not os.path.exists('.\\config.json'):
        with open(f".\\config.json", 'w', encoding='utf-8') as def_c:
            json.dump(CONFIG_DEFAULT, def_c)
            setts = CONFIG_DEFAULT
    else:
        try:
            with open(f'.\\config.json', 'r', encoding='utf-8') as load_j:
                setts = json.load(load_j)
        except:
            with open(f".\\config.json", 'w', encoding='utf-8') as def_c:
                json.dump(CONFIG_DEFAULT, def_c)
                setts = CONFIG_DEFAULT
    if setts.get('save_directory'):
        try:
            os.mkdir(setts.get('save_directory'))
        except Exception as e:
            # print(e)
            pass
    return setts


def save_setts(settings):
    with open('.\\config.json', 'w', encoding='utf-8') as file:
        json.dump(settings, file)
