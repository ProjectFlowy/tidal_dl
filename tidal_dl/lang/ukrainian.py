#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ukrainian.py
@Time    :   2022/02/20
@Author  :   Montyzzz & 9uyone
@Version :   1.2
@Contact :   ---
@Desc    :   
'''


class LangUkrainian(object):
    SETTING = "НАЛАШТУВАННЯ"
    VALUE = "ЗНАЧЕННЯ"
    SETTING_DOWNLOAD_PATH = "Шлях завантаження"
    SETTING_ONLY_M4A = "Перетворювати mp4 на m4a"
    SETTING_ADD_EXPLICIT_TAG = "Додавати тег Нецензурно"
    SETTING_ADD_HYPHEN = "Додавати дефіс"
    SETTING_ADD_YEAR = "Додавати рік перед ім'ям папки альбому"
    SETTING_USE_TRACK_NUM = "Додавати номер треку"
    SETTING_AUDIO_QUALITY = "Якість аудіо"
    SETTING_VIDEO_QUALITY = "Якість відео"
    SETTING_CHECK_EXIST = "Перевіряти наявність"
    SETTING_ARTIST_BEFORE_TITLE = "Виконавець перед назвою треку"
    SETTING_ALBUMID_BEFORE_FOLDER = "ID перед назвою папки"
    SETTING_INCLUDE_EP = "Включати сингли та міньйони (EP)"
    SETTING_SAVE_COVERS = "Зберігати обкладинки"
    SETTING_LANGUAGE = "Мова"
    SETTING_USE_PLAYLIST_FOLDER = "Використовувати папку плейлиста"
    SETTING_MULITHREAD_DOWNLOAD = "Багатопоточне завантаження"
    SETTING_ALBUM_FOLDER_FORMAT = "Формат папки альбому"
    SETTING_TRACK_FILE_FORMAT = "Формат файлу треку"
    SETTING_SHOW_PROGRESS = "Показувати прогрес"
    SETTING_SHOW_TRACKIFNO = "Показувати інформацію про трек"
    SETTING_SAVE_ALBUMINFO = "Зберігати AlbumInfo.txt"
    SETTING_ADD_LYRICS = "Додавати тексти пісень"
    SETTING_LYRICS_SERVER_PROXY = "Проксі для сервера з текстами пісень"
    SETTING_PATH = "Шлях налаштувань"
    SETTINGS_ADD_LRC_FILE = "Зберігати тексти з відмітками часу (.lrc файл)"
    SETTING_APIKEY = "Підтримка ключа API"
    SETTING_ADD_TYPE_FOLDER = "Додавати папку-тип"

    CHOICE = "ВИБІР"
    FUNCTION = "ФУНКЦІЇ"
    CHOICE_ENTER = "Ввід"
    CHOICE_ENTER_URLID = "Ввід 'URL/ID':"
    CHOICE_EXIT = "Вихід"
    CHOICE_LOGIN = "Перевірити AccessToken"
    CHOICE_SETTINGS = "Налаштування"
    CHOICE_SET_ACCESS_TOKEN = "Застосувати власний AccessToken"
    CHOICE_DOWNLOAD_BY_URL = "Завантажити за URL-адресою або ідентифікатором"
    CHOICE_LOGOUT = "Деавторизація"
    CHOICE_APIKEY = "Вибрати ключ API"

    PRINT_ERR = "[ПОМИЛКА]"
    PRINT_INFO = "[ІНФОРМАЦІЯ]"
    PRINT_SUCCESS = "[УСПІХ]"

    PRINT_ENTER_CHOICE = "Вибір вводу:"
    PRINT_LATEST_VERSION = "Остання версія:"
    # PRINT_USERNAME = "ім'я користувача:"
    # PRINT_PASSWORD = "пароль:"

    CHANGE_START_SETTINGS = "Запуск налаштувань('0'-Повернутися,'1'-Так):"
    CHANGE_DOWNLOAD_PATH = "Шлях завантаження('0'-не змінювати):"
    CHANGE_AUDIO_QUALITY = "Якість аудіо('0'-Звичайна,'1'-Висока,'2'-HiFi,'3'-MQA):"
    CHANGE_VIDEO_QUALITY = "Якість відео(1080,720,480,360):"
    CHANGE_ONLYM4A = "Перетворювати mp4 на m4a('0'-Ні,'1'-Так):"
    CHANGE_ADD_EXPLICIT_TAG = "Додавати тег 'Нецензурно'('0'-Ні,'1'-Так):"
    CHANGE_ADD_HYPHEN = "Використати дефіс замість пробілів в іменах файлів('0'-Ні,'1'-Так):"
    CHANGE_ADD_YEAR = "Додавати рік до назв тек альбомів('0'-Ні,'1'-Так):"
    CHANGE_USE_TRACK_NUM = "Додавати номер доріжки перед назвами файлів('0'-Ні,'1'-Так):"
    CHANGE_CHECK_EXIST = "Перевіряти наявний файл перед завантаженням треку('0'-Ні,'1'-Так):"
    CHANGE_ARTIST_BEFORE_TITLE = "Додати ім’я виконавця перед заголовком треку('0'-Ні,'1'-Так):"
    CHANGE_INCLUDE_EP = "Включати сингли та міньйони під час завантаження альбомів виконавця('0'-Ні,'1'-Так):"
    CHANGE_ALBUMID_BEFORE_FOLDER = "Додати ідентифікатор перед текою альбому('0'-Ні,'1'-Так):"
    CHANGE_SAVE_COVERS = "Зберігати обкладинки('0'-Ні,'1'-Так):"
    CHANGE_LANGUAGE = "Обрати мову"
    CHANGE_ALBUM_FOLDER_FORMAT = "Формат теки альбому('0'-не змінювати):"
    CHANGE_TRACK_FILE_FORMAT = "Формат файлу треку('0'-не змінювати):"
    CHANGE_SHOW_PROGRESS = "Показувати прогрес('0'-Ні,'1'-Так):"
    CHANGE_SHOW_TRACKINFO = "Показувати інформацію про трек('0'-Ні,'1'-Так):"
    CHANGE_SAVE_ALBUM_INFO = "Зберігати AlbumInfo.txt('0'-Ні,'1'-Так):"
    CHANGE_ADD_LYRICS = "Додавати тексти пісень('0'-Ні,'1'-Так):"
    CHANGE_LYRICS_SERVER_PROXY = "Проксі для сервера з текстами пісень('0'-не змінювати):"
    CHANGE_ADD_LRC_FILE = "Зберігати тексти пісень з відмітками часу в .lrc файл('0'-Ні,'1'-Так):"
    CHANGE_ADD_TYPE_FOLDER = "Додавати теку-тип,наприклад Альбом/Відео/Плейлист('0'-Ні,'1'-Так):"

    # {} are required in these strings
    AUTH_START_LOGIN = "Початок процесу авторизації..."
    AUTH_LOGIN_CODE = "Ваш логін-код: {}"
    AUTH_NEXT_STEP = "Зайдіть на {} протягом наступних {} для завершення налаштування."
    AUTH_WAITING = "Очікування авторизації..."
    AUTH_TIMEOUT = "Час очікування минув."

    MSG_VALID_ACCESSTOKEN = "AccessToken хороший упродовж {}."
    MSG_INVAILD_ACCESSTOKEN = "Термін дії AccessToken'а закінчився. Пробуємо оновити його."
    MSG_PATH_ERR = "Невірний шлях!"
    MSG_INPUT_ERR = "Помилка введення!"

    MODEL_ALBUM_PROPERTY = "АЛЬБОМ-ВЛАСТИВІСТЬ"
    MODEL_TRACK_PROPERTY = "ТРЕК-ВЛАСТИВІСТЬ"
    MODEL_VIDEO_PROPERTY = "ВІДЕО-ВЛАСТИВІСТЬ"
    MODEL_ARTIST_PROPERTY = "АРТИСТ-ВЛАСТИВІСТЬ"
    MODEL_PLAYLIST_PROPERTY = "ПЛЕЙЛИСТ-ВЛАСТИВІСТЬ"

    MODEL_TITLE = 'Назва'
    MODEL_TRACK_NUMBER = 'Номер доріжки'
    MODEL_VIDEO_NUMBER = 'Номер відео'
    MODEL_RELEASE_DATE = 'Дата релізу'
    MODEL_VERSION = 'Версія'
    MODEL_EXPLICIT = 'Нецензурно'
    MODEL_ALBUM = 'Альбом'
    MODEL_ID = 'ID'
    MODEL_NAME = 'Ім\'я'
    MODEL_TYPE = 'Тип'
