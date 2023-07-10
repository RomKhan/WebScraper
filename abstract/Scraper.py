import random
from bs4 import BeautifulSoup, SoupStrainer
import time
import re

from abstract.ScraperAbstract import ScraperAbstract


class Scraper(ScraperAbstract):
    def __init__(self, url_components, link_token, image_loader, data_saver, by_settings, page_load_indicator, website_name, city, listing_type, prev_address = None):
        ScraperAbstract.__init__(self, by_settings, page_load_indicator, data_saver, website_name, city, listing_type)
        self.url_components = url_components
        self.link_token = link_token
        self.prev_address = prev_address
        self.image_loader = image_loader
        self.links = {}
        self.is_first_run = True

    def run(self):
        driver = self.get_webdriver()

        future_previous_idx = set()
        for i in range(10):
            if self.is_first_run and i > 1:
                self.is_first_run = False
                break
            url = self.get_desk_link()
            self.run_driver_on_page(url, driver)
            soup = self.get_soap(driver.page_source)
            links = self.get_offer_links(soup)
            idx = set(links.keys())

            if i == 0:
                future_previous_idx = idx

            idx = idx.difference(self.previous_idx)
            for id in idx:
                self.links[id] = links[id]

            self.current_page += 1
            if i == 9:
                print('Я взял обявления с 10 страниц')
            if len(idx) != len(set(links.keys())):
                break

        print(f'Пытаюсь спарсить {len(self.links)} обявлений')
        self.current_page = 1
        self.previous_idx = future_previous_idx
        self.get_offers_data(driver)

        self.delete_webdriver(driver)

    def get_offer_data(self, link, id, driver):
        pass

    def get_offers_data(self, driver):
        idx = list(self.links.keys())
        for id in idx:
            t1 = time.time()
            link, errors = self.links.pop(id)
            if not self.get_offer_data(link, id, driver) and errors < 10:
                self.links[id] = (link, errors + 1)
            t2 = time.time()
            if t2-t1 < 8:
                time.sleep(random.randint(5, 8))
            t2 = time.time()
            print(f'Парсинг обьявления {link} занял {t2-t1} секунд')

    def get_offer_links(self, soup):
        links = {}
        for link in soup:
            if link.has_attr('href') and self.link_token in link['href']:
                id = list(filter(None, re.split('_|/', link['href'])))[-1]
                if re.match('^[0-9]{5,}', id):
                    if self.prev_address is not None:
                        links[id] = (self.prev_address + link['href'], 0)
                    else:
                        links[id] = (link['href'], 0)
        return links

    def get_soap(self, content):
        soup = BeautifulSoup(content, parse_only=SoupStrainer('a'), features="html.parser")
        return soup

    async def parse_offer_page(self, content, link, id):
        pass