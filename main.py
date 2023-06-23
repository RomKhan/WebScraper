import random
import threading

import yadisk
from selenium import webdriver
from bs4 import BeautifulSoup, SoupStrainer
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from AvitoScraper import AvitoScraper
from CianScrapeAll import CianScrapeAll
from CianScraper import CianScraper
from DataWorker import DataWorker
from DomClickScraper import DomClickScraper
from ImageLoader import ImageLoader
import os
import re
import shutil


def parse_cian(urls, city_link_match, appearing_mask, image_loader, data_saver):
    sort_mask = sorted(range(len(appearing_mask)), key=lambda k: appearing_mask[k])
    finish_times = [0 for x in range(len(appearing_mask))]
    scrapers = []

    if not os.path.exists("cian"):
        os.mkdir('cian')

    for i in range(len(urls)):
        url_components = CianScraper.parse_link(urls[i])
        offer_link_indicator = 'cian.ru/sale/flat'
        pics_folder = 'cian'
        scraper = CianScraper(url_components, offer_link_indicator, pics_folder, image_loader, data_saver)
        scrapers.append(scraper)

    while True:
        for i in sort_mask:
            t1 = time.time()
            if t1 - finish_times[i] > (appearing_mask[i] - 5)*60:
                print(f'Парсю обялвения с города: {city_link_match[i]}')
                scrapers[i].run()
                t2 = time.time()
                finish_times[i] = t2
                wait = random.randint(50, 240)
                time.sleep(wait)
        time.sleep(random.randint(appearing_mask[sort_mask[0]]-5, appearing_mask[sort_mask[0]]+5) * 60)


def main():
    if os.path.exists("domclick"):
        shutil.rmtree("domclick")
    if os.path.exists("avito"):
        shutil.rmtree("avito")

    disk = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
    disk.token = 'y0_AgAAAAANYmzbAAf07QAAAADl13LC72bkYNO7So6osrxeT1dmwOorZhQ'

    url_cian = 'https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=1&sort=creation_date_desc'
    url_yandex = 'https://realty.ya.ru/moskva/kupit/kvartira/?sort=DATE_DESC'
    url_domclick = 'https://domclick.ru/search?deal_type=sale&category=living&offer_type=flat&sort=published&sort_dir=desc&offset=0'
    url_avito = 'https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ?s=104'

    # image_loader = ImageLoader(disk=disk)
    # image_thread = threading.Thread(target=image_loader.load_images_parallel)
    # image_thread.start()

    data_saver = DataWorker()
    data_thread = threading.Thread(target=data_saver.run)
    data_thread.start()

    t1 = time.time()
    url_cian_moscow = 'https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=2&region=1&sort=creation_date_desc'
    url_cian_peter = 'https://spb.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=2&region=2&sort=creation_date_desc'
    url_cian_ekb = 'https://ekb.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=2&region=4743&sort=creation_date_desc'
    # urls = [url_cian_moscow, url_cian_peter, url_cian_ekb]
    # city_link_match = ['Москва', 'Питер', 'Екатеринбург']
    # # Раз в сколько минут нужно делать запрос для каждой ссылке.
    # appearing_mask = [15, 30, 60]
    # parse_cian(urls, city_link_match, appearing_mask, image_loader, data_saver)

    url_cian_peter = 'https://spb.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&maxprice=6000000&minprice=5000000&offer_type=flat&p=2&region=2&sort=creation_date_desc'
    url = CianScrapeAll.parse_link(url_cian_peter)
    if not os.path.exists("cian"):
        os.mkdir('cian')
    scraper = CianScrapeAll(url, data_saver)
    while not scraper.is_end:
        scraper.iter()
    t2 = time.time()
    print(f'Удалось спарсить {scraper.count_of_parsed} обявлений, '
          f'было отправлено {scraper.count_of_requests} запросов за {t2-t1} секунд')




    #PROXY = "92.255.7.162:8080"

    # t1 = time.time()
    # os.mkdir('domclick')
    # scraper1 = DomClickScraper(url_domclick, 'card', 'domclick', image_loader)
    # thread1 = threading.Thread(target=scraper1.run)
    # #thread1.start()
    # time.sleep(5)
    #
    # os.mkdir('avito')
    # scraper3 = AvitoScraper(url_avito, '/moskva/kvartiry/', 'avito', 'https://www.avito.ru', image_loader)
    # thread3 = threading.Thread(target=scraper3.run)
    # #thread3.start()

    #thread1.join()
    # thread2.join()
    #thread3.join()
    t2 = time.time()
    print(f'work time - {t2 - t1}')
    data_saver.is_run = False
    data_thread.join()
    # image_loader.is_run = False
    # image_thread.join()
    t2 = time.time()
    print(f'work time - {t2 - t1}')




if __name__ == '__main__':
    main()
