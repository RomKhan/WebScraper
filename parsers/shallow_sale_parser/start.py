import os
import threading
import time

import requests

from utils import *
from parsers.AvitoScrapeAll import AvitoScrapeAll
from parsers.CianScrapeAll import CianScrapeAll
from parsers.DomClickScrapeAll import DomClickScrapeAll
from parsers.YandexScrapeAll import YandexScrapeAll


def main():
    logging.info(f'Количество активных потоков: {threading.active_count()}')
    server_url = 'http://db-api-service:8080'
    # server_url = 'http://192.168.100.53:30058/db'
    connected = False
    while not connected:
        try:
            requests.get(f'{server_url}/ping')  # Пример запроса к Flask-серверу
            connected = True
        except requests.ConnectionError:
            print('Flask server is not available. Retrying in 5 seconds...')
            time.sleep(1)

    print('pass the ping')

    website_name = os.environ.get('WEBSITE_NAME')
    type = os.environ.get('TYPE')
    # website_name='yandex'
    # type='sale'

    # if is_exist(website_name, type):
    #     return

    if website_name == 'cian':
        parse_all(CianScrapeAll, website_name, type)
    elif website_name == 'domclick':
        parse_all(DomClickScrapeAll, website_name, type)
    elif website_name == 'avito':
        parse_all(AvitoScrapeAll, website_name, type)
    elif website_name == 'yandex':
        parse_all(YandexScrapeAll, website_name, type)


if __name__ == '__main__':
    main()