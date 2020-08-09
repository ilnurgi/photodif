import json
import os

DEBUG = False

VERSION = '0.0.2'
SOFT_NAME = 'photodif'

DIR_BASE = os.path.dirname(__file__)
DIR_START_LEFT = os.path.expanduser('~')
DIR_START_RIGHT = os.path.expanduser('~')

SETTINGS_PATH = os.path.join(DIR_BASE, 'settings.json')

AVAILABLE_FILE_ENDS = {
    '.jpg', 'png'
}

DATE_TIME_FORMAT_NEW_FILE = '%Y%m%d_%H%M%S'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_TIME_FORMAT_EXIF = '%Y:%m:%d %H:%M:%S'

# загружаем настройки из файла
if os.path.exists(SETTINGS_PATH):
    globals().update(json.load(open(SETTINGS_PATH, encoding='utf-8')))


def write(**kwargs):
    """
    записывает настройки в файл
    """
    json.dump(
        kwargs,
        open(SETTINGS_PATH, 'w', encoding='utf-8'),
        indent=4,
        ensure_ascii=False)
