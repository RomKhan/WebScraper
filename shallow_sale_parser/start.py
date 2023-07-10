import os
import time

import requests

from utils import parse_all
from parsers.AvitoScrapeAll import AvitoScrapeAll
from parsers.CianScrapeAll import CianScrapeAll
from parsers.DomClickScrapeAll import DomClickScrapeAll


def main():
    server_url = 'http://app:8080'
    connected = False
    while not connected:
        try:
            requests.get(f'{server_url}/ping')  # Пример запроса к Flask-серверу
            connected = True
        except requests.ConnectionError:
            print('Flask server is not available. Retrying in 5 seconds...')
            time.sleep(1)

    url_cian_moscow = 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&maxprice=8000000&minprice=100000&offer_type=flat&p=2&region=1&sort=creation_date_desc'
    url_domclick_moscow = 'https://domclick.ru/search?deal_type=sale&category=living&offer_type=flat&offer_type=layout&sale_price__lte=10000000&sort=published&sort_dir=desc&sale_price__gte=100000&offset=0'
    url_avito_moscow = 'https://www.avito.ru/moskva/kvartiry/prodam?bt=1&pmax=10000000&pmin=100000&p=1&s=104'

    website_name = os.environ.get('WEBSITE_NAME')
    city = os.environ.get('CITY')
    if website_name == 'циан':
        parse_all(CianScrapeAll, url_cian_moscow, city, 'Продажа', website_name)
    elif website_name == 'домклик':
        parse_all(DomClickScrapeAll, url_domclick_moscow, city, 'Продажа', website_name)
    elif website_name == 'авито':
        parse_all(AvitoScrapeAll, url_avito_moscow, city, 'Продажа', website_name)

if __name__ == '__main__':
    main()