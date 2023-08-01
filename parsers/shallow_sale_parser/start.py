import os
import time

import requests

from utils import parse_all
from parsers.AvitoScrapeAll import AvitoScrapeAll
from parsers.CianScrapeAll import CianScrapeAll
from parsers.DomClickScrapeAll import DomClickScrapeAll
from parsers.YandexScrapeAll import YandexScrapeAll


def main():
    server_url = 'http://db-api-service:8080'
    connected = False
    while not connected:
        try:
            requests.get(f'{server_url}/ping')  # Пример запроса к Flask-серверу
            connected = True
        except requests.ConnectionError:
            print('Flask server is not available. Retrying in 5 seconds...')
            time.sleep(1)

    print('pass the ping')

    url_cian_moscow = 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&maxprice=8000000&minprice=100000&offer_type=flat&p=2&region=1&sort=price_object_order'
    url_domclick_moscow = 'https://domclick.ru/search?deal_type=sale&category=living&offer_type=flat&offer_type=layout&sale_price__lte=7000000&sort=price&sort_dir=asc&sale_price__gte=10000&offset=0'
    url_avito_moscow = 'https://www.avito.ru/moskva/kvartiry/prodam?bt=1&pmax=10000000&pmin=100000&p=1&s=1'
    url_yandex_moscow = 'https://realty.ya.ru/moskva/kupit/kvartira/?sort=PRICE&priceMin=1000000&page=1'

    website_name = os.environ.get('WEBSITE_NAME')
    city = os.environ.get('CITY')
    if website_name == 'cian':
        parse_all(CianScrapeAll, url_cian_moscow, city, website_name, 'Продажа')
    elif website_name == 'domclick':
        parse_all(DomClickScrapeAll, url_domclick_moscow, city, website_name, 'Продажа')
    elif website_name == 'avito':
        parse_all(AvitoScrapeAll, url_avito_moscow, city, website_name, 'Продажа')
    elif website_name == 'yandex':
        parse_all(YandexScrapeAll, url_yandex_moscow, city, website_name, 'Продажа')

if __name__ == '__main__':
    main()