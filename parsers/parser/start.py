import os
import threading
import time

import requests

from utils import *
from shallow_parsers.ShallowAvitoScraper import ShallowAvitoScraper
from shallow_parsers.ShallowCianScraper import ShallowCianScraper
from shallow_parsers.ShallowDomclickScraper import ShallowDomclickScraper
from shallow_parsers.ShallowYandexScraper import ShallowYandexScraper
from deep_parsers.DeepCianScraper import DeepCianScraper
from deep_parsers.DeepAvitoScraper import DeepAvitoScraper
from deep_parsers.DeepDomclickScraper import DeepDomclickScraper
from deep_parsers.DeepYandexScraper import DeepYandexScraper


def main():
    server_url = 'http://db-api-service:8080'
    # server_url = 'http://192.168.100.53:30802/db'
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
    mode = os.environ.get('MODE')
    # website_name='cian'
    # type='sale'
    # mode = 'deep'

    if mode == 'shallow':
        if website_name == 'cian':
            shallow_parser(ShallowCianScraper, website_name, type)
        elif website_name == 'domclick':
            shallow_parser(ShallowDomclickScraper, website_name, type)
        elif website_name == 'avito':
            shallow_parser(ShallowAvitoScraper, website_name, type)
        elif website_name == 'yandex':
            shallow_parser(ShallowYandexScraper, website_name, type)
    elif mode == 'deep':
        if website_name == 'cian':
            deep_parser(DeepCianScraper, website_name, type)
        elif website_name == 'domclick':
            deep_parser(DeepDomclickScraper, website_name, type)
        elif website_name == 'avito':
            deep_parser(DeepAvitoScraper, website_name, type)
        elif website_name == 'yandex':
            deep_parser(DeepYandexScraper, website_name, type)



if __name__ == '__main__':
    main()